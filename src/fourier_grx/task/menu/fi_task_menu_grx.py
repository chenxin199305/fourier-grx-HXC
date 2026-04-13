from enum import IntEnum


class TaskMenuGRX(IntEnum):
    """
    TaskMenuGRX is a IntEnum class that defines the task types for the robot.

    Range:
    900 - 999: reserved for the GRX robot

    主要设计用于定义 GRX 系列产品的通用任务类型。
    """
    TASK_DEMO = 900

    TASK_SET_HOME = 999

    TASK_TEST_JOINT_PID = 901
    TASK_TEST_JOINT_PD = 902
    TASK_TEST_FRICTION_PID = 903
    TASK_TEST_FRICTION_PD = 904

    TASK_APPLICATION_STAND_MOTION_CONTROL = 960
    TASK_APPLICATION_WALK_MOTION_CONTROL = 965  # Jason 2025-03-20: hope to "walk" 965, not 996 :D
    TASK_APPLICATION_RUN_MOTION_CONTROL = 966
    TASK_APPLICATION_WALK_MOTION_BANK = 967
    TASK_APPLICATION_CLIMB_UP_MOTION_CONTROL = 968
    TASK_APPLICATION_FREQUENCY_MOTION_CONTROL = 969
