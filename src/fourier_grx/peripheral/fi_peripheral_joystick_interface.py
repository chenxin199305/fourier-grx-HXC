from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_joystick import PeripheralJoystick, PeripheralJoystickType

peripheral_joystick: PeripheralJoystick | None = None

if gl_config.parameters.get("peripheral", {}).get("use_joystick", False):

    joystick_type = \
        gl_config.parameters.get("peripheral", {}).get("joystick_type",
                                                       PeripheralJoystickType.XBOX)

    try:
        peripheral_type = PeripheralJoystickType(joystick_type)
        peripheral_joystick = PeripheralJoystick(peripheral_type)

    except ValueError:
        Logger().print_error(f"Peripheral joystick type error: {joystick_type}")
