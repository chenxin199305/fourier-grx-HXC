from fourier_core.logger import *
from fourier_core.predefine import *


def thread_peripheral_init() -> FunctionResult:
    from fourier_grx.peripheral import peripheral_joystick, peripheral_keyboard

    Logger().print_info("peripheral_init start...")

    if peripheral_joystick is not None:
        peripheral_joystick.enable()

    if peripheral_keyboard is not None:
        peripheral_keyboard.enable()

    Logger().print_info("peripheral_init finish!")

    return FunctionResult.SUCCESS


def thread_peripheral_deinit() -> FunctionResult:
    from fourier_grx.peripheral import peripheral_joystick, peripheral_keyboard

    Logger().print_info("peripheral_deinit start...")

    if peripheral_joystick is not None:
        peripheral_joystick.disable()

    if peripheral_keyboard is not None:
        peripheral_keyboard.disable()

    Logger().print_info("peripheral_deinit finish!")

    return FunctionResult.SUCCESS
