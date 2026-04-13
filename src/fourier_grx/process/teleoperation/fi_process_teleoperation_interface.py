from fourier_core.predefine import *


def teleoperation_init() -> FunctionResult:
    from fourier_grx.process.teleoperation.fi_process_teleoperation import process_teleoperation_init

    process_teleoperation_init()

    return FunctionResult.SUCCESS


def teleoperation_deinit() -> FunctionResult:
    from fourier_grx.process.teleoperation.fi_process_teleoperation import process_teleoperation_deinit

    process_teleoperation_deinit()

    return FunctionResult.SUCCESS
