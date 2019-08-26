# project based on
# http://github.com/timestocome

from ev3dev2.auto import *

# init of motors
m_right = LargeMotor(OUTPUT_A)
m_left = LargeMotor(OUTPUT_B)
arm = MediumMotor(OUTPUT_D)


# init Sound
sound = Sound()

actions = ['center_forward', 'hard_right_forward', 'right_forward', 'left_forward', 'hard_left_forward',
           'center_reverse', 'hard_right_reverse', 'right_reverse', 'left_reverse', 'hard_left_reverse',
           'move_arm', 'run_forever', 'full_stop']


def center_forward():
    forward()


def hard_right_forward():
    right_turn_90()
    run_forever()


def right_forward():
    right_turn_45()
    run_forever()


def left_forward():
    left_turn_45()
    run_forever()


def hard_left_forward():
    left_turn_90()
    run_forever()


def center_reverse():
    reverse()


def hard_right_reverse():
    right_turn_90()
    reverse()


def right_reverse():
    right_turn_45()
    reverse()


def left_reverse():
    left_turn_45()
    reverse()


def hard_left_reverse():
    left_turn_90()
    reverse()


def full_stop():
    m_right.stop()
    m_left.stop()


def run_forever():
    m_right.run_forever(speed_sp=300)
    m_left.run_forever(speed_sp=300)


def move_arm():
    arm.on_for_rotations(speed=40, rotations=0.5)
    arm.wait_while('running')
    sound.speak(text='Gotch yaaaa', play_type=0)
    arm.on_for_rotations(speed=40, rotations=-0.5)
    arm.wait_while('running')


def forward():
    m_right.run_timed(time_sp=5000, speed_sp=100)
    m_left.run_timed(time_sp=5000, speed_sp=100)
    m_right.wait_while('running')
    m_left.wait_while('running')


def reverse():
    m_right.run_timed(time_sp=3000, speed_sp=-100)
    m_left.run_timed(time_sp=3000, speed_sp=-100)
    m_right.wait_while('running')
    m_left.wait_while('running')


def right_turn_90():
    m_right.on_for_rotations(speed=40, rotations=-1)
    m_left.on_for_rotations(speed=40, rotations=1)
    m_right.wait_while('running')
    m_left.wait_while('running')


def right_turn_45():
    m_right.on_for_rotations(speed=40, rotations=-0.5)
    m_left.on_for_rotations(speed=40, rotations=0.5)
    m_right.wait_while('running')
    m_left.wait_while('running')


def left_turn_90():
    m_right.on_for_rotations(speed=40, rotations=1)
    m_left.on_for_rotations(speed=40, rotations=-1)
    m_right.wait_while('running')
    m_left.wait_while('running')


def left_turn_45():
    m_right.on_for_rotations(speed=40, rotations=0.5)
    m_left.on_for_rotations(speed=40, rotations=-0.5)
    m_right.wait_while('running')
    m_left.wait_while('running')
