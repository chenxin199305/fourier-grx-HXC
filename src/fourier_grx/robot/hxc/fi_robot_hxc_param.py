import numpy


class RobotHXCParam:
    # sensor
    number_of_sensor_imu = 1

    # joint
    number_of_joint = 3 + 3 + 3 + 3 + 1 + 1 + 1 + 1

    joints_direction = numpy.array([
        1.0, 1.0, 1.0,  # front left leg (position control)
        1.0, 1.0, 1.0,  # front right leg (position control)
        1.0, 1.0, 1.0,  # rear left leg (position control)
        1.0, 1.0, 1.0,  # rear right leg (position control)
        1.0,  # front left leg (velocity control)
        1.0,  # front right leg (velocity control)
        1.0,  # rear left leg (velocity control)
        1.0,  # rear right leg (velocity control)
    ])
    joint_home_position = numpy.zeros(number_of_joint)
    joint_max_position = +numpy.pi * numpy.ones(number_of_joint)
    joint_min_position = -numpy.pi * numpy.ones(number_of_joint)
    joint_reduction_ratio = numpy.ones(number_of_joint)
    joint_kinematic_reduction_ratio = numpy.ones(number_of_joint)
    joint_kinetic_reduction_ratio = numpy.ones(number_of_joint)
    joint_control_mode = numpy.zeros(number_of_joint)
    joint_pd_control_kp = numpy.array([
        60.0, 60.0, 60.0,  # front left leg (position control)
        60.0, 60.0, 60.0,  # front right leg (position control)
        60.0, 60.0, 60.0,  # rear left leg (position control)
        60.0, 60.0, 60.0,  # rear right leg (position control)
        0.0,  # front left leg (velocity control)
        0.0,  # front right leg (velocity control)
        0.0,  # rear left leg (velocity control)
        0.0,  # rear right leg (velocity control)
    ])
    joint_pd_control_kd = numpy.array([
        3.0, 3.0, 3.0,  # front left leg (position control)
        3.0, 3.0, 3.0,  # front right leg (position control)
        3.0, 3.0, 3.0,  # rear left leg (position control)
        3.0, 3.0, 3.0,  # rear right leg (position control)
        10.0,  # front left leg (velocity control)
        10.0,  # front right leg (velocity control)
        10.0,  # rear left leg (velocity control)
        10.0,  # rear right leg (velocity control)
    ])

    # --------------------------------------------------

    number_of_leg_body_joints = 3 + 3 + 3 + 3
    number_of_wheel_body_joints = 1 + 1 + 1 + 1
    number_of_whole_body_joints = number_of_joint

    indexes_of_leg_body_joints = numpy.array([
        0, 1, 2,  # front left leg (position control)
        3, 4, 5,  # front right leg (position control)
        6, 7, 8,  # rear left leg (position control)
        9, 10, 11,  # rear right leg (position control)
    ])
    indexes_of_wheel_body_joints = numpy.array([
        12,  # front left leg (velocity control)
        13,  # front right leg (velocity control)
        14,  # rear left leg (velocity control)
        15,  # rear right leg (velocity control)
    ])
    indexes_of_whole_body_joints = numpy.array(
        indexes_of_leg_body_joints.tolist() + indexes_of_wheel_body_joints.tolist()
    )


class RobotHXCT1Param(RobotHXCParam):
    joints_direction = numpy.array([
        1.0, 1.0, 1.0,  # front left leg (position control)
        1.0, -1.0, 1.0,  # front right leg (position control)
        1.0, 1.0, 1.0,  # rear left leg (position control)
        1.0, -1.0, 1.0,  # rear right leg (position control)
        1.0,  # front left leg (velocity control)
        1.0,  # front right leg (velocity control)
        1.0,  # rear left leg (velocity control)
        1.0,  # rear right leg (velocity control)
    ])
