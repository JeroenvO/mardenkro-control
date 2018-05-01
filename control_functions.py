from math import tan, pi

MAX_SPEED_DIFF = 250
ARM_CENTER = 500   # #ticks for center of arm.
WHEEL_BASE = 0.7  # Distance between wheels in m.
mu_1 = 1  # how much speed slowdown based on large angle
# mu_2 = 1  # not used. replaced by ARM_M_PER_STEP = 0.125 / 500
mu_3 = 25  # correction for high angle to motor-speed
mu_4 = 0.05  # compensation for arm too far from center
n_1 = 1  # power for angle with mu_1
n_2 = 1  # power for arm offset with mu_4


def control_arm(old_arm, offset):
    """
    Calculate new position of the arm, in meters

    :param old_arm: current position of the arm in meter
    :param offset: meters distance between nozzle and line below nozzle
    :return: new position of the arm in meter
    """
    return old_arm + offset


def control_direction(angle, arm):
    """
    Control difference between left and right motors

    :param angle: angle of camera line
    :param arm: new position of arm in ticks
    :return: relative speed difference in left/right motors
    """
    angle_correction = round(WHEEL_BASE * tan(angle) * mu_3)
    arm_correction = -round(mu_4 * (arm - ARM_CENTER)) #** n_2
    # arm_correction = 0
    print('arm: {} angle_c: {}, arm_c: {}'.format(arm, angle_correction, arm_correction))
    return angle_correction + arm_correction


def control_speed(setpoint, angle):
    """
    Set the speed based on the setpoint and angle.

    :param setpoint: desired (maximum) speed.
    :param angle: Angle of the line seen by the camera
    :return:

    """
    return round(setpoint * 1 / (1 + (abs(angle) ** n_1) * mu_1))


def accuracy_good(l_nlines, l_angle, arm, a_right, o_right, a_left, o_left):
    """


    :param l_nlines:
    :param l_angle:
    :param arm:
    :param a_right:
    :param o_right:
    :param a_left:
    :param o_left:
    :return:
    """
    if l_nlines < 20:
       return [False, 'Not enough lines.']

    if abs(l_angle) > pi/4:
        return [False, 'Angle too large']
    #
    # if abs(o_right - a_right) > MAX_SPEED_DIFF:  # [0-250]
    #     return [False, 'Right motor difference too large! Setpoint {}, reading {}'.format(o_right, a_right)]
    #
    # if abs(o_left - a_left) > MAX_SPEED_DIFF:  # [0-250]
    #     return [False, 'Left motor difference too large! Setpoint {}, reading {}'.format(o_left, a_left)]

    return [True, '']
