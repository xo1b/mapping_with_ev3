import matplotlib as mpl
mpl.use('Agg')

from ev3dev2.auto import *
import ev3_rl_actions
import wheel
import numpy as np
from math import pi, cos, sin
import matplotlib.pyplot as plt

#initialize ev3dev
m_right = LargeMotor(OUTPUT_A)
m_left = LargeMotor(OUTPUT_B)
arm = MediumMotor(OUTPUT_D)
us = UltrasonicSensor()
ts = TouchSensor()
gyro = GyroSensor()
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

def calc_pos():
    global xdata
    global ydata
    global ang_data
    global rot_r_arr
    global rot_l_arr

    #getting the rotations for calculating the distance
    rot_new_r = m_right.rotations
    rot_r_arr = np.append(rot_r_arr, [rot_new_r])

    rot_new_l = m_left.rotations
    rot_l_arr = np.append(rot_l_arr, [rot_new_l])

    start_r = rot_r_arr[-2]
    start_l = rot_l_arr[-2]
    end_r = rot_r_arr[-1]
    end_l = rot_l_arr[-1]

    #the average is calculated to avoid positive distance while only turning
    rotations = ((end_r - start_r) + (end_l - start_l))/2

    # calculating the distance travelled, 40,7 is the diameter of the wheel
    distance = rotations*(40.7*pi)

    #preparing the calcuation of the kathedes
    #to get the coordinates the distance is the hypotenuse of a right-angled triangle
    ang_new = gyro.angle
    ang_data = np.append(ang_data, [ang_new])
    alpha = ang_data[-2]-ang_data[-1]
    sin_a = sin(alpha)

    #avoid that distance is 0 when alpha is 0 (moving straight forward)
    if sin_a == 0:
        sin_a == 1
    else:
        pass

    #actually calculating
    gegenkath = distance * sin(alpha) #calculating side opposed to angle alpha
    ankath = distance * cos(alpha) #calculating side which lies on alpha

    #updating coordinates
    x_new = xdata[-1]+gegenkath
    y_new = ydata[-1]+ankath

    #update array with coordinates
    xdata = np.append(xdata, [x_new])
    ydata = np.append(ydata, [y_new])

    #plot if an obstacle is nearby
    if us.value() > 500:
        pass
    else:
        draw_plot()

    #return xdata, ydata, ang_data, rot

def draw_plot():
    global xdata
    global ydata

    x = xdata[-1]+us.value()
    y = ydata[-1]+us.value()

    try:
        plt.imread('map.png')
        plt.plot(x, y, 'ro')
        plt.savefig('map.png')
    except:
        plt.plot(x, y, 'ro')
        plt.savefig('map.png')




#xdata=xdata, ydata=ydata, ang_data=ang_data, rot=rot