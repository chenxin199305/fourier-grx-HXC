from enum import IntEnum


class FlashState(IntEnum):
    NONE = 0x00
    IN_PROCESS = 0x01
    FREE = 0x02
