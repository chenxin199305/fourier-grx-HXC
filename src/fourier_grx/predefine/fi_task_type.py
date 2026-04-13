from enum import IntEnum


class TaskType(IntEnum):
    """
    用于区分任务类型的枚举类

    - IDLE：空闲任务，实际并不产生什么作用的任务
    - NORMAL：普通任务，用于执行一些普通的任务，循环执行
    - ONESHOT：一次性任务，只执行一次的任务，执行完后会自动切换到其他任务
    """
    IDLE = 0
    NORMAL = 1
    ONESHOT = 2
