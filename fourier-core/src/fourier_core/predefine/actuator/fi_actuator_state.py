from enum import IntEnum


class ActuatorState(IntEnum):
    NONE = 0x00
    NORMAL = 0x01
    WARNING = 0x02
    FAULT = 0x03
