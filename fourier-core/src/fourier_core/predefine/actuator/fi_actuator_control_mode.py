from enum import IntEnum


class ActuatorControlMode(IntEnum):
    """
    Actuator control mode enumeration.

    For unify the control mode of different types of actuator,
    then convenient to control the actuator in fourier-core.
    """

    NONE = 0x00

    CURRENT = 0x01
    EFFORT = 0x02
    VELOCITY = 0x03
    POSITION = 0x04
    TRAPEZOIDAL = 0x05
    PD = 0x06
    TRAJECTORY = 0x07

    SERVO_ON = 0x10
    SERVO_OFF = 0x11
    SERVO_REBOOT = 0x12
    SERVO_ZERO = 0x13  # 相对编码器清零

    SET_HOME = 0x21
    FIND_HOME = 0x22
    SET_PID = 0x23

    CLEAR_FAULT = 0x31
    GET_PARAM = 0x32
    SET_PARAM = 0x33
    GET_CONFIG = 0x34
    SET_CONFIG = 0x35

    ABSOLUTE_ZERO = 0x40  # 绝对编码器清零
