from enum import IntEnum


class ControlSystemWorkState(IntEnum):
    NONE = 0x00
    IAP = 0x01
    APP = 0x02
    EXE = 0x03
    LINUX_EXE = 0x04
