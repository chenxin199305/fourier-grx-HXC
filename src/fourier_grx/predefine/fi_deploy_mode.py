from enum import IntEnum


class DeployMode(IntEnum):
    DEFAULT = 0
    DEVELOPER_MODE = 1
    AGV_MODE = 2
    UPPER_BODY_MODE = 3
    LOWER_BODY_MODE = 4
    OPERATION_MODE = 5
    SDK_MODE = 6
