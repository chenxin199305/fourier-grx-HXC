from fourier_core.predefine import *
from fourier_grx.comm.fi_dynalink_manager import (
    DynalinkManager,
)

from fourier_grx.comm.hex.fi_comm_manager_v3_frame import (
    CommManagerV3Frame,
)
from fourier_grx.comm.hex.fi_comm_operation_result import (
    CommOperationResult,
)
from fourier_grx.comm.hex.fi_comm_parameter_type import (
    CommParameterType,
    CommParameterTypeSize,
)


class CommManagerV3Communication:
    NONE = 0x00000000
    HEART_BEAT = 0x01010101
    ERROR_CODE = 0x07FFFFFF
    SYSTEM_ERROR = 0x06FFFFFF

    def __init__(self):
        self.operation_result_ = 0
        self.parameter_count_ = 0
        self.parameters_ = []

    def decode(self, frame: CommManagerV3Frame):
        response_frame = CommManagerV3Frame(data=frame.data)  # copy from request frame

        def set_response(result=None, param_type=None, param_size=None, params=None):
            """
            Set response frame parameters
            Parameters
            ----------
            result: CommOperationResult | None
            param_type: CommParameterType | None
            param_size: CommParameterTypeSize | None
            params: list | None

            Returns
            -------
            None
            """
            if result is not None:
                response_frame.operation_result = result

            if param_type is not None:
                response_frame.set_parameter_type(param_type)

            if param_size is not None:
                response_frame.set_parameter_size(param_size)

            if params is not None:
                response_frame.set_parameters(params)

        # default response
        set_response(CommOperationResult.FAIL, CommParameterType.NONE, 0 * CommParameterTypeSize.NONE, [])

        match frame.operation_mode:
            case CommManagerV3Communication.NONE:
                set_response(CommOperationResult.SUCCESS, CommParameterType.NONE, 0 * CommParameterTypeSize.NONE, [])

            case CommManagerV3Communication.HEART_BEAT:
                DynalinkManager().dynalink_comm.flag_heart_beat = FlagState.SET

                set_response(CommOperationResult.SUCCESS, CommParameterType.NONE, 0 * CommParameterTypeSize.NONE, [])

            case CommManagerV3Communication.ERROR_CODE:
                set_response(CommOperationResult.SUCCESS, CommParameterType.NONE, 0 * CommParameterTypeSize.NONE, [])

        return response_frame
