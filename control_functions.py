ARM_CENTER = 500
mu_1 = 1  # how much speed slowdown based on large angle
# mu_2 = 1  # not used. replaced by ARM_M_PER_STEP = 0.125 / 500
mu_3 = 1  # correction for high angle to motor-speed
mu_4 = 1  # compensation for arm too far from center
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
    return mu_3 * angle + mu_4 * (arm - ARM_CENTER) ** n_2
