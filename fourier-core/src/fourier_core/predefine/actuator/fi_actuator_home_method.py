from enum import IntEnum


class ActuatorHomeMethod(IntEnum):
    HOME_IS_CURRENT_POSITION = 0x01
    HOME_IS_CURRENT_POSITION_MOVE_TO_NEW_ZERO = 0x02
