from fourier_core.predefine import *


def streamlit_init() -> FunctionResult:
    from fourier_grx.process.streamlit import process_streamlit_init

    process_streamlit_init()

    return FunctionResult.SUCCESS


def streamlit_deinit() -> FunctionResult:
    from fourier_grx.process.streamlit import process_streamlit_deinit

    process_streamlit_deinit()

    return FunctionResult.SUCCESS
