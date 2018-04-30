import math

# defines
ARM_M_PER_STEP = 0.125 / 500
# camera calibrations in meters.
CAMERA_WIDTH_BOTTOM = 0.43
CAMERA_WIDTH_TOP = 1.58
CAMERA_TO_NOZZLE = .41
CAMERA_HEIGHT = 1.35


def ci_arm(arm):
    """
    Correct arm from steps to meters
    12.5cm per 500steps

    :param arm: input arm in steps [50-900]
    :return: arm distance in meters
    """

    return (arm - 50) * ARM_M_PER_STEP


def co_arm(arm):
    """
    Calculate arm postition to steps
    12.5cm per 500steps

    :param arm: in meters
    :return: in steps [50-900]
    """
    return arm / ARM_M_PER_STEP + 50


def ci_offset(offset, angle):
    """
    Calculate offset postition of camera to meters
    and correct for offset of sprayer to camera

    :param offset: in camera range [-1 to 1]
    :param angle: radians of top angle of detected line
    :return: nozzle wrong position in meters
    """
    o_offset_camera = offset * CAMERA_WIDTH_BOTTOM/2 + CAMERA_WIDTH_BOTTOM/2
    o_offset_nozzle = math.tan(angle)*CAMERA_TO_NOZZLE
    return o_offset_camera + o_offset_nozzle
