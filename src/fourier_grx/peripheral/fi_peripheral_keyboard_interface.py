from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_keyboard import PeripheralKeyboard, PeripheralKeyboardType

peripheral_keyboard: PeripheralKeyboard | None = None

if gl_config.parameters.get("peripheral", {}).get("use_keyboard", False):

    keyboard_type = \
        gl_config.parameters.get("peripheral", {}).get("keyboard_type",
                                                       PeripheralKeyboardType.STANDARD)

    try:
        peripheral_type = PeripheralKeyboardType(keyboard_type)
        peripheral_keyboard = PeripheralKeyboard(peripheral_type)

    except ValueError:
        Logger().print_error(f"Peripheral keyboard type error: {keyboard_type}")
