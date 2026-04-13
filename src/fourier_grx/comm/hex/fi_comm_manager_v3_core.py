import fourier_grx.comm.hex.fi_comm_tool as fi_comm_tool
from fourier_grx.comm.fi_dynalink_manager import DynalinkManager

from fourier_grx.comm.hex.fi_comm_manager_v3_frame import CommManagerV3Frame
from fourier_grx.comm.hex.fi_comm_operation_result import CommOperationResult
from fourier_grx.comm.hex.fi_comm_parameter_type import CommParameterType, CommParameterTypeSize


class CommManagerV3APP:
    SOFTWARE_VERSION = 0x10010102

    def __init__(self):
        pass

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
            case CommManagerV3APP.SOFTWARE_VERSION:
                parameters = []
                parameters.extend(fi_comm_tool.int_to_array(DynalinkManager().dynalink_core.software_version, size=4)[1])
                set_response(CommOperationResult.SUCCESS, CommParameterType.INT, 1 * CommParameterTypeSize.INT, parameters)

        return response_frame
