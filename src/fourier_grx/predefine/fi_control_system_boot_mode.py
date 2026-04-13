from enum import IntEnum


class ControlSystemBootMode(IntEnum):
    NONE = 0x00
    IAP = 0x01
    APP = 0x02
    EXE = 0x03
    LINUX = 0x04
    WINDOWS = 0x05
    MACOS = 0x06
