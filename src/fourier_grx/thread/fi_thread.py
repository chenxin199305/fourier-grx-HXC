from fourier_core.predefine import *


def thread_init() -> FunctionResult:
    from fourier_grx.thread.peripheral.fi_thread_peripheral import thread_peripheral_init

    thread_peripheral_init()

    return FunctionResult.SUCCESS


def thread_deinit() -> FunctionResult:
    from fourier_grx.thread.peripheral.fi_thread_peripheral import thread_peripheral_deinit

    thread_peripheral_deinit()

    return FunctionResult.SUCCESS
