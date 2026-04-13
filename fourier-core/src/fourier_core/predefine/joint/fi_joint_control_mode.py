from enum import IntEnum


class JointControlMode(IntEnum):
    """
    Joint control mode enumeration.

    For unify the control mode of different types of joints,
    """

    NONE = 0x00

    CURRENT = 0x01
    EFFORT = 0x02
    VELOCITY = 0x03
    POSITION = 0x04

    PD = 0x06

    POSITION_PSEUDO_PD = 0x09
    OTHER = 0x0A
