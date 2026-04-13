from enum import IntEnum


class FunctionResult(IntEnum):
    SUCCESS = 0
    FAIL = -1
    RUNNING = 1
    PREPARE = 2
    EXECUTE = 3
    NOT_EXECUTE = 4
    TIMEOUT = 5
    NOT_IMPLEMENTED = 6
