from enum import IntEnum


class IAPErrorCode(IntEnum):
    NONE = 0x00
    WRITE_FLASH_ERROR = 0x01
    READ_FLASH_ERROR = 0x02
    VERIFY_FAIL = 0x04
