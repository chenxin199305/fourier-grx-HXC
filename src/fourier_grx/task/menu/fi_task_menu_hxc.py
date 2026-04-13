from enum import IntEnum


class TaskMenuHXC(IntEnum):
    """
    TaskMenuHXC is a IntEnum class that defines the task types for the robot.

    Range:
    3000 - 3999: reserved for the HXC robot
    """

    TASK_LEG_BODY_RL_WALK_AIRTIME = 3100
    TASK_LEG_BODY_RL_WALK_CPG = 3101

    TASK_WHOLE_BODY_STAND_CONTROL = 3300
    TASK_WHOLE_BODY_RL_WALK_CPG = 3302
    TASK_WHOLE_BODY_STEER_DRIVE = 3303
