from fourier_core.predefine import *


def dds_init() -> FunctionResult:
    from fourier_grx.process.dds.fi_process_dds import process_dds_init

    process_dds_init()

    return FunctionResult.SUCCESS


def dds_deinit() -> FunctionResult:
    from fourier_grx.process.dds.fi_process_dds import process_dds_deinit

    process_dds_deinit()

    return FunctionResult.SUCCESS
