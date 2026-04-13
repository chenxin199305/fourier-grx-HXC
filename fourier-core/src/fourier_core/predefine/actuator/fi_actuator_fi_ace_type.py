from enum import IntEnum


class ActuatorFIACEType(IntEnum):
    """
    Actuator ACE type enumeration.
    """
    NONE = 0

    ACE_TYPE_X6_60 = 101
    ACE_TYPE_X10_40 = 102
