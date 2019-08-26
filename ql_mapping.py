##!/usr/bin/env python3

"""
# based on
# http://github.com/timestocome

things, which got ignored or assumed:
The robot is a tank, but I couldn't figure out how ot measure the distance by using the classes mdiff or tank.
I assumed that the left

things to do:
change rewards, finding objects should be rewarded
integrate coordinates
adapt q-function (state depends on coordinates)
"""



import numpy as np
from pathlib import Path
import cmath
from ev3dev2.auto import *
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.sensor.lego import TouchSensor
import ev3_rl_actions
import coordinates
import datetime

#initialize ev3dev
m_right = LargeMotor(OUTPUT_A)
m_left = LargeMotor(OUTPUT_B)
arm = MediumMotor(OUTPUT_D)
us = UltrasonicSensor()
gyro = GyroSensor()
ts = TouchSensor
sound = Sound()

us.MODE_US_DIST_CM = 'US_DIST_CM'
gyro.MODE_GYRO_ANG = 'GYRO-ANG'

# define actions, move to class
actions = ev3_rl_actions.actions

#empty arrays to store position data later on
xdata = np.array([0])
ydata = np.array([0])
ang_start = gyro.angle
ang_data = np.array([ang_start])
rot_r = m_right.rotations
rot_l = m_left.rotations
rot_r_arr = np.array([rot_r])
rot_l_arr = np.array([rot_l])



# robot environment
def get_distance():
    # returns distance 1-50
    distance = us.value()
    return int(distance)

def object_detect(distance, min_distance, reward):
    ev3_rl_actions.run_forever()
    while us.value() > min_distance:
        pass
    else:
        ev3_rl_actions.full_stop()
        dist_new = us.value()
        if distance <= dist_new:
            reward +=1
        else:
            reward += 0


# robot actions
def move(action, distance):
    reward = 0.001
    min_distance = 250


    # penalty for being too closes to an obstacle
    if distance <= min_distance:  # buffer zone in cm
        reward -= min_distance / distance


    # get reward for moving or robot will eventually park itself in middel of the room
    if action == 0:
        object_detect(distance, min_distance, reward)
        reward += 2  # reward robot for covering distance
    elif action == 1:
        ev3_rl_actions.center_reverse()
        dist_new = us.value()
        if dist_new > min_distance:
            reward += 2
        else:
            reward += 0.0# discourage reverse, no sensors on back of robot
    elif action == 2:
        ev3_rl_actions.right_turn_90()
        object_detect(distance, min_distance, reward)
    elif action == 3:
        ev3_rl_actions.left_turn_90()
        object_detect(distance, min_distance, reward)
    elif action == 4:
        ev3_rl_actions.left_turn_90()
        reward += 1
    elif action == 5:
        ev3_rl_actions.right_turn_90()
        reward += 1
    elif action == 6:
        ev3_rl_actions.move_arm()
        sound.speak(text='how should I get out of this? how?', play_type=0)
        dist_new = us.value()
        if distance <= dist_new:
            reward +=1
        else:
            reward += 2
    elif action == 7:
        ev3_rl_actions.run_forever()
        while us.value() > min_distance:
            reward += 2
            pass
        else:
            ev3_rl_actions.full_stop()
            reward -= 0.0
    elif action == 8:
        ev3_rl_actions.right_turn_45()
        dist_new = us.value()
        if distance <= dist_new:
            reward +=1
        else:
            reward += 2
    elif action == 9:
        ev3_rl_actions.left_turn_45()
        dist_new = us.value()
        if distance <= dist_new:
            reward += 1
        else:
            reward += 2
    elif action == 10:
        sound.speak(text='I want this to end!')
        ev3_rl_actions.run_forever()
        while us.value() >= min_distance:
            pass
        else:
            ev3_rl_actions.full_stop()
            reward += 1
    elif action == 11:
        ev3_rl_actions.hard_right_reverse()
        reward =- 1
    elif action == 12:
        ev3_rl_actions.hard_left_reverse()
        reward -= 1

    print("distance %d,  action %d,  reward %d" % (distance, action, reward))

    return reward


###############################################################################
# q learning happens here
###############################################################################

# training vars
lr = 0.1  # learning rate
gamma = 0.9  # memory (gamma^n_steps)
n_loops = 500  # training loops to perform

"""
the state is in this changed version defined by the coordinates. to transform x and y into a single unique
number the coordinates are transformed into a complex number. 
"""

max_distance = 2550
x_states = n_loops +1 #the number of states depends on the loops, because the state is determinded by the coordinates
y_states = x_states
n_actions = len(actions)

# new q-table
def init_q_table(x_states, y_states, n_actions):
    table = np.zeros((x_states, y_states, n_actions))
    return table


# load saved q table
def load_q_table():
    t_1d = np.load('qTable.npy')
    table = t_1d.reshape(x_states, y_states, n_actions)
    return table


def save_q_table(t):
    t_1d = t.reshape(x_states * y_states * n_actions, 1)
    np.save('qTable.npy', t_1d)


def choose_action(x, y, q_table, epsilon):
    state_actions = q_table[x][y][:]

    # random move or no data recorded for this state yet
    if (np.random.uniform() < epsilon) or (np.sum(state_actions) == 0):
        action_chose = np.random.randint(n_actions)
        # epsilon *= .99         # lots of random searching when table is zero
        if epsilon > 0.1: epsilon *= 0.8
    else:
        action_chose = state_actions.argmax()

    return action_chose


def rl():
    global xdata
    global ydata

    x = xdata[-1]
    y = ydata[-1]


    # init new table if none found
    saved_table = Path('qTable.npy')
    if saved_table.is_file():
        q_table = load_q_table()
    else:
        q_table = init_q_table(x_states, y_states, n_actions)

    epsilon = 1.0  # random choice % decreases over time

    n_steps = 0
    dist = us.value()

    while n_steps < n_loops:
        start = datetime.datetime.now()
        print('step %d epsilon %lf' %(n_steps, epsilon))

        # chose action and move robot
        a = choose_action(x, y, q_table, epsilon)
        reward = move(a, dist)

        #run the coordinatens and mapping before updating qTable
        coordinates.calc_pos()

        # update state
        x_next = xdata[-1]
        y_next = ydata[-1]

        # what robot thought would happen next
        q_predict = q_table[x][y][a]

        # what actually happened
        q_target = reward + gamma * q_table[x][y][a]

        # update q_table
        q_table[x][y][a] += lr * (q_target - q_predict)

        # wrap up
        x = x_next
        y = y_next

        n_steps += 1

        # save data
        if n_steps % 100 == 0:
            save_q_table(q_table)

        # print(datetime.datetime.now() - start)

    return q_table


###############################################################################
# clean shut down of hardware
###############################################################################
#def cleanup():
    # distance_finder.cleanup()
    # ev3_rl_actions.cleanup()


###############################################################################
# run code
###############################################################################

q_table = rl()

# cleanup()

'''
#q_table = load_q_table()
print('--------------------------------')
print('Final Q Table')
for i in range(n_distance_states):
    for j in range(n_cat_states):
        print('distance %d, cat %d' %(i, j))
        print('action values', q_table[i, j, :])

'''

# save_q_table()
# load_q_table()


