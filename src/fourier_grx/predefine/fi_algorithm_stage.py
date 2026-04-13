from enum import IntEnum


class AlgorithmStage(IntEnum):
    """
    FSMItem stage enumeration.

    Attributes:
        STAGE_INIT (int): change from other task to this task.
        STAGE_START (int): change from this task to this task again.
        STAGE_PROCESS_01 (int): process 1.
        STAGE_PROCESS_02 (int): process 2.
        STAGE_PROCESS_03 (int): process 3.
        STAGE_PROCESS_04 (int): process 4.
        STAGE_PROCESS_05 (int): process 5.
        STAGE_WARM_UP (int): warm up.
        STAGE_ERROR (int): error.
        STAGE_SUCCESS (int): success.
        STAGE_FINISH (int): finish.
    """
    STAGE_INIT = -1
    STAGE_START = 0
    STAGE_PROCESS_01 = 1
    STAGE_PROCESS_02 = 2
    STAGE_PROCESS_03 = 3
    STAGE_PROCESS_04 = 4
    STAGE_PROCESS_05 = 5
    STAGE_PROCESS_06 = 6
    STAGE_PROCESS_07 = 7
    STAGE_PROCESS_08 = 8
    STAGE_PROCESS_09 = 9
    STAGE_PROCESS_10 = 10
    STAGE_PROCESS_11 = 11
    STAGE_PROCESS_12 = 12
    STAGE_PROCESS_13 = 13
    STAGE_PROCESS_14 = 14
    STAGE_PROCESS_15 = 15
    STAGE_PROCESS_16 = 16
    STAGE_PROCESS_17 = 17
    STAGE_PROCESS_18 = 18
    STAGE_PROCESS_19 = 19
    STAGE_PROCESS_20 = 20
    STAGE_WARM_UP = 90
    STAGE_RUN = 91
    STAGE_PAUSE = 92
    STAGE_ERROR = 98
    STAGE_SUCCESS = 99
    STAGE_FINISH = 100
    STAGE_SWITCH = 101  # Special stage for switching to another task
