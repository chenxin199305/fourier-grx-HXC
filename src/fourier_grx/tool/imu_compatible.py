import numpy

from .fi_tool_logger import Logger


def euler_angle_ypr_to_quat(euler_angle_rpy):
    """
    Convert Euler angle (RPY) to Quaternion (XYZW) using YPR rotation sequence.

    Input:
    - euler_angle: Euler angle (RPY) [deg]

    Output:
    - quat: Quaternion (XYZW)
    """
    euler_angle = numpy.deg2rad(euler_angle_rpy)

    roll = euler_angle[0] / 2
    pitch = euler_angle[1] / 2
    yaw = euler_angle[2] / 2

    cy = numpy.cos(yaw)
    sy = numpy.sin(yaw)
    cp = numpy.cos(pitch)
    sp = numpy.sin(pitch)
    cr = numpy.cos(roll)
    sr = numpy.sin(roll)

    quat_x = sr * cp * cy - cr * sp * sy
    quat_y = cr * sp * cy + sr * cp * sy
    quat_z = cr * cp * sy - sr * sp * cy
    quat_w = cr * cp * cy + sr * sp * sy

    quat = numpy.array([quat_x, quat_y, quat_z, quat_w])

    return quat


def imu_installation_compatible(
        installation_upright=True,
        imu_quat=numpy.array([0, 0, 0, 1]),
        imu_euler_angle=numpy.array([0, 0, 0]),
        imu_angular_velocity=numpy.array([0, 0, 0]),
        imu_acceleration=numpy.array([0, 0, 0]),
):
    """
    Please check DEMO.md for imu installation direction info.
    In default, the IMU installation direction is not upright in GR1T1 and GR1T2 robot.
    However, we would plan to make the IMU installation direction upright in the future.
    So, this function is used to compatible with different IMU installation direction.

    Input:
    - installation_upright: True or False
    - imu_quat: Quaternion (XYZW)
    - imu_euler_angle: Euler angle (ZYX) [deg]
    - imu_angular_velocity: Angular velocity (XYZ) [deg/s]
    - imu_acceleration: Linear acceleration (XYZ) [m/s^2]

    Output:
    - compatible_imu_quat: Quaternion (XYZW)
    - compatible_imu_euler_angle: Euler angle (ZYX) [deg]
    - compatible_imu_angular_velocity: Angular velocity (XYZ) [deg/s]
    - compatible_imu_acceleration: Linear acceleration (XYZ) [m/s^2]
    """
    compatible_imu_quat = imu_quat
    compatible_imu_euler_angle = imu_euler_angle
    compatible_imu_angular_velocity = imu_angular_velocity
    compatible_imu_acceleration = imu_acceleration

    # ------------------------------
    if installation_upright is True:
        # upright installation direction
        # quat (x, y, z, w)
        compatible_imu_quat = numpy.array(
            [-compatible_imu_quat[1], compatible_imu_quat[0], compatible_imu_quat[2], compatible_imu_quat[3]]
        )

        # euler angle (rpy)
        compatible_imu_euler_angle_roll = -compatible_imu_euler_angle[0]
        compatible_imu_euler_angle_pitch = compatible_imu_euler_angle[1]
        compatible_imu_euler_angle_yaw = compatible_imu_euler_angle[2]
        compatible_imu_euler_angle = numpy.array(
            [compatible_imu_euler_angle_roll, compatible_imu_euler_angle_pitch, compatible_imu_euler_angle_yaw]
        )

        # angular velocity (xyz)
        compatible_imu_angular_velocity = numpy.array(
            [
                -compatible_imu_angular_velocity[1],
                compatible_imu_angular_velocity[0],
                compatible_imu_angular_velocity[2],
            ]
        )
        # linear acceleration (xyz)
        compatible_imu_acceleration = numpy.array(
            [-compatible_imu_acceleration[1], compatible_imu_acceleration[0], compatible_imu_acceleration[2]]
        )

    else:
        # Default GR1T1 and GR1T2 IMU installation direction: upside down installation direction
        # quat (x, y, z, w)
        compatible_imu_quat = numpy.array(
            [-compatible_imu_quat[3], -compatible_imu_quat[2], compatible_imu_quat[0], -compatible_imu_quat[1]]
        )

        # euler angle (rpy)
        compatible_imu_euler_angle_roll = (
            180 - compatible_imu_euler_angle[0]
            if compatible_imu_euler_angle[0] > 0
            else -180 - compatible_imu_euler_angle[0]
        )
        compatible_imu_euler_angle_pitch = compatible_imu_euler_angle[1]
        compatible_imu_euler_angle_yaw = compatible_imu_euler_angle[2]
        compatible_imu_euler_angle = numpy.array(
            [compatible_imu_euler_angle_roll, compatible_imu_euler_angle_pitch, compatible_imu_euler_angle_yaw]
        )

        # angular velocity (xyz)
        compatible_imu_angular_velocity = numpy.array(
            [
                -compatible_imu_angular_velocity[1],
                -compatible_imu_angular_velocity[0],
                -compatible_imu_angular_velocity[2],
            ]
        )
        # linear acceleration (xyz)
        compatible_imu_acceleration = numpy.array(
            [-compatible_imu_acceleration[1], -compatible_imu_acceleration[0], -compatible_imu_acceleration[2]]
        )
    # ------------------------------

    return compatible_imu_quat, compatible_imu_euler_angle, compatible_imu_angular_velocity, compatible_imu_acceleration


if __name__ == "__main__":
    """
    Test imu_installation_compatible code
    """
    imu_quat = numpy.array([0, 0, 0, 1])
    imu_euler_angle = numpy.array([150, 0, 0])
    imu_angular_velocity = numpy.array([0, 0, 0])
    imu_acceleration = numpy.array([0, 0, 0])

    compatible_imu_quat, compatible_imu_euler_angle, compatible_imu_angular_velocity, compatible_imu_acceleration = (
        imu_installation_compatible(
            installation_upright=False,
            imu_quat=imu_quat,
            imu_euler_angle=imu_euler_angle,
            imu_angular_velocity=imu_angular_velocity,
            imu_acceleration=imu_acceleration,
        )
    )
    Logger().print_info("compatible_imu_quat = ", compatible_imu_quat)
    Logger().print_info("compatible_imu_euler_angle = ", compatible_imu_euler_angle)
    Logger().print_info("compatible_imu_angular_velocity = ", compatible_imu_angular_velocity)
    Logger().print_info("compatible_imu_acceleration = ", compatible_imu_acceleration)
