from enum import IntEnum


class ActuatorFIACEControlMode(IntEnum):
    """
    Actuator control mode enumeration.

    Customized for ACE.
    """

    NONE = 0

    # mode of operation (added in ACE v1.0)
    CURRENT = 4
    VELOCITY = 3
    POSITION = 1

    # mode of operation (added in ACE v2.0)
    EFFORT = 2
    PD = 7
    BREAK = 8

    # functions (added in ACE v1.0)
    SERVO_ON = 0x10
    SERVO_OFF = 0x11
    SERVO_REBOOT = 0x12
    SERVO_ZERO = 0x13  # 相对编码器清零

    SET_PID = 0x23

    CLEAR_FAULT = 0x31
    SET_PARAM = 0x32
    SET_CONFIG = 0x33

    # functions (added in ACE v2.0)
    ABSOLUTE_ZERO = 0x40  # 绝对编码器清零
