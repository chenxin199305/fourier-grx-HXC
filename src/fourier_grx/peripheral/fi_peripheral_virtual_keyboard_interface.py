from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_keyboard import PeripheralVirtualKeyboard

peripheral_virtual_keyboard: PeripheralVirtualKeyboard | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_keyboard", False):

    try:
        peripheral_virtual_keyboard = PeripheralVirtualKeyboard()

        Logger().print_success(f"Peripheral virtual keyboard connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual keyboard connect error")
