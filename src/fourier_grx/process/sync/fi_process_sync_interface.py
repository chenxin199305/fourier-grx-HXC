from fourier_core.predefine import *


def sync_init() -> FunctionResult:
    from fourier_grx.process.sync.fi_process_sync import process_sync_init

    process_sync_init()

    return FunctionResult.SUCCESS


def sync_deinit() -> FunctionResult:
    from fourier_grx.process.sync.fi_process_sync import process_sync_deinit

    process_sync_deinit()

    return FunctionResult.SUCCESS
