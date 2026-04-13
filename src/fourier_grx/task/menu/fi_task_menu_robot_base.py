from enum import IntEnum


class TaskMenuRobotBase(IntEnum):
    """
    TaskMenuRobotBase is a IntEnum class that defines the task types for the robot.

    Range:
    000 - 100: reserved for the RobotBase class
    """
    TASK_NONE = 0
    TASK_IDLE = 1

    TASK_TEST_ROBOT_BASE = 2

    TASK_JOINT_EFFORT_CONTROL = 11
    TASK_JOINT_VELOCITY_CONTROL = 12
    TASK_JOINT_POSITION_CONTROL = 13
    TASK_JOINT_MIX_CONTROL = 14

    TASK_END_EFFECTOR_EFFORT_CONTROL = 21
    TASK_END_EFFECTOR_VELOCITY_CONTROL = 22
    TASK_END_EFFECTOR_POSITION_CONTROL = 23
    TASK_END_EFFECTOR_MIX_CONTROL = 24
