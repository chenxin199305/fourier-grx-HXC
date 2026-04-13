from fourier_core.predefine import *


def rerun_init() -> FunctionResult:
    from fourier_grx.process.rerun import process_rerun_init

    process_rerun_init()

    return FunctionResult.SUCCESS


def rerun_deinit() -> FunctionResult:
    from fourier_grx.process.rerun import process_rerun_deinit

    process_rerun_deinit()

    return FunctionResult.SUCCESS
