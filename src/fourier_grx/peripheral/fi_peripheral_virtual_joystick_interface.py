from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_joystick import PeripheralVirtualJoystick

peripheral_virtual_joystick: PeripheralVirtualJoystick | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_joystick", False):

    try:
        peripheral_virtual_joystick = PeripheralVirtualJoystick()

        Logger().print_success(f"Peripheral virtual joystick connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual joystick connect error")
