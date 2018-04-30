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
    :param arm: new position of arm in meters
    :return: relative speed difference in left/right motors
    """

