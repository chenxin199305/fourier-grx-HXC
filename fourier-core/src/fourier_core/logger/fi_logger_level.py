from enum import IntEnum


class LoggerLevel(IntEnum):
    NONE = 0x00
    TRACE = 0x01
    DEBUG = 0x02
    INFO = 0x03
    SUCCESS = 0x04
    WARNING = 0x05
    ERROR = 0x06
    CRITICAL = 0x07
