from enum import IntEnum

from .fi_actuator_control_mode import ActuatorControlMode


class ActuatorModeOfOperation(IntEnum):
    """
    Actuator mode of operation enumeration.

    In the CiA 402 standard, the value of mode of operation can be customized.
    So we define the mode of operation enumeration here (match with ActuatorControlMode).
    """
    NONE = ActuatorControlMode.NONE.value
    CURRENT = ActuatorControlMode.CURRENT.value
    EFFORT = ActuatorControlMode.EFFORT.value
    VELOCITY = ActuatorControlMode.VELOCITY.value
    POSITION = ActuatorControlMode.POSITION.value
    TRAPEZOIDAL = ActuatorControlMode.TRAPEZOIDAL.value
    PD = ActuatorControlMode.PD.value
