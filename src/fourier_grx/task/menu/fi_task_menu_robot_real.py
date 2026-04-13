from enum import IntEnum


class TaskMenuRobotReal(IntEnum):
    """
    TaskMenuRobotReal is a IntEnum class that defines the task types for the robot.

    Range:
    101 - 200: reserved for the RobotReal class
    """
    TASK_TEST_ROBOT_REAL = 101

    """
    Jason 2026-02-01:
    历史遗留原因，这些任务编号是从 RobotBase 继承过来的，
    因此编号范围仍然是 000 - 100。
    未来可能会进行重构。
    """
    TASK_FIND_HOME = 31
    TASK_SET_HOME = 32
    TASK_CLEAR_ALARM = 33
    TASK_CLEAR_FAULT = 34
    TASK_SERVO_ON = 35
    TASK_SERVO_OFF = 36
    TASK_PAUSE_MOTION = 37
    TASK_SENSOR_CALIBRATION = 38
    TASK_SENSOR_SOFTWARE_VERSION = 39
    TASK_SET_CONFIG = 40
    TASK_SERVO_REBOOT = 41
    TASK_SERVO_ZERO = 42
    TASK_REMOTE_CONTROL = 43
    TASK_FIX_POSITION = 44
    TASK_WAIT = 45
