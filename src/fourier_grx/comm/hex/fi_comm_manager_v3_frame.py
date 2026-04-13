import numpy
import fourier_grx.comm.hex.fi_comm_tool as fi_comm_tool

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.comm.hex.fi_comm_parameter_type import CommParameterType


class CommManagerV3Frame:
    FRAME_HEADER_BUFFER = [0x70, 0x71, 0x72, 0x73]
    FRAME_TAIL_BUFFER = [0x7F]
    FRAME_HEADER = 0x70717273
    FRAME_TAIL = 0x7F

    LENGTH_OF_FRAME_HEADER = 4
    LENGTH_OF_PROTOCOL_VERSION = 1
    LENGTH_OF_DATA_SECTION_LENGTH = 4
    LENGTH_OF_DATA_SECTION = 256
    LENGTH_OF_DATA_SECTION_CHECKSUM = 1
    LENGTH_OF_FRAME_TAIL = 1

    LENGTH_OF_FUNCTION_TYPE = 4
    LENGTH_OF_OPERATION_MODE = 4
    LENGTH_OF_READ_WRITE = 1
    LENGTH_OF_OPERATION_RESULT = 1
    LENGTH_OF_PARAMETER_TYPE = 1
    LENGTH_OF_PARAMETER_SIZE = 4

    def __init__(self, data=None):
        if data is None:
            self.data = []
            self.frame_header = 0
            self.protocol_version = 0
            self.data_section_length = 0
            self.data_section = []
            self.funcation_type = 0
            self.operation_mode = 0
            self.read_write = 0
            self.operation_result = 0
            self.parameter_type = 0
            self.parameter_size = 0
            self.parameters = []
            self.check_sum = 0
            self.frame_tail = 0
        else:
            self.data = data
            self.update_from_data()

    def update_from_data(self):
        # frame header
        frame_header_buffer = self.data[
                              0:
                              CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                              ]
        tool_result, self.frame_header = fi_comm_tool.array_to_int(frame_header_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame header error!")

        # protocol version
        protocol_version_buffer = self.data[
                                  CommManagerV3Frame.LENGTH_OF_FRAME_HEADER:
                                  CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                  + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                  ]
        tool_result, self.protocol_version = fi_comm_tool.array_to_int(protocol_version_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame protocol version error!")

        # data section length
        data_section_length_buffer = self.data[
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION:
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                     + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                                     ]
        tool_result, self.data_section_length = fi_comm_tool.array_to_int(data_section_length_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame data section length error!")

        # data section
        self.data_section = self.data[
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH:
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                            + self.data_section_length
                            ]

        function_type_buffer = self.data_section[
                               0:
                               CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                               ]
        tool_result, self.funcation_type = fi_comm_tool.array_to_int(function_type_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame function type error!")

        operation_mode_buffer = self.data_section[
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE:
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                ]
        tool_result, self.operation_mode = fi_comm_tool.array_to_int(operation_mode_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame operation_mode mode error!")

        read_write_buffer = self.data_section[
                            CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE:
                            CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                            + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                            ]
        tool_result, self.read_write = fi_comm_tool.array_to_int(read_write_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame read write error!")

        operation_result_buffer = self.data_section[
                                  CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                  + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                  + CommManagerV3Frame.LENGTH_OF_READ_WRITE:
                                  CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                  + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                  + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                                  + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                                  ]
        tool_result, self.operation_result = fi_comm_tool.array_to_int(operation_result_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame operation_mode result error!")

        parameter_type_buffer = self.data_section[
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT:
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                                + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                                ]
        tool_result, self.parameter_type = fi_comm_tool.array_to_int(parameter_type_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame parameter type error!")

        parameter_size_buffer = self.data_section[
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                                + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE:
                                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                                + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                                + CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE
                                ]
        tool_result, self.parameter_size = fi_comm_tool.array_to_int(parameter_size_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame parameter count error!")

        parameters_buffer = self.data_section[
                            CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                            + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                            + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                            + CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE:
                            CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                            + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                            + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                            + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                            + CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE
                            + self.parameter_size * 4
                            ]

        self.parameters = parameters_buffer
        # if self.parameter_type == CommParameterType.NONE:
        #     pass
        # elif self.parameter_type == CommParameterType.CHAR:
        #     for i in range(int(len(parameters_buffer) / 1)):
        #         tool_result, parameter = \
        #             fi_comm_tool.array_to_int(parameters_buffer[i * 1 + 0: i * 1 + 1])
        #         if tool_result == FunctionResult.SUCCESS:
        #             self.parameters.append(parameter)
        #         else:
        #             self.parameters.append(0)
        # elif self.parameter_type == CommParameterType.SHORT:
        #     for i in range(int(len(parameters_buffer) / 2)):
        #         tool_result, parameter = \
        #             fi_comm_tool.array_to_int(parameters_buffer[i * 2 + 0: i * 2 + 2])
        #         if tool_result == FunctionResult.SUCCESS:
        #             self.parameters.append(parameter)
        #         else:
        #             self.parameters.append(0)
        # elif self.parameter_type == CommParameterType.INT:
        #     for i in range(int(len(parameters_buffer) / 4)):
        #         tool_result, parameter = \
        #             fi_comm_tool.array_to_int(parameters_buffer[i * 4 + 0: i * 4 + 4])
        #         if tool_result == FunctionResult.SUCCESS:
        #             self.parameters.append(parameter)
        #         else:
        #             self.parameters.append(0)
        # elif self.parameter_type == CommParameterType.FLOAT:
        #     for i in range(int(len(parameters_buffer) / 4)):
        #         tool_result, parameter = \
        #             fi_comm_tool.array_to_float(parameters_buffer[i * 4 + 0: i * 4 + 4])
        #         if tool_result == FunctionResult.SUCCESS:
        #             self.parameters.append(parameter)
        #         else:
        #             self.parameters.append(0)
        # else:
        #     Logger().print_error("CommManagerV3Frame _update_from_data parameter type error")

        # data section checksum
        data_section_checksum_buffer = self.data[
                                       CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                       + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                       + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                                       + self.data_section_length:
                                       CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                       + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                       + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                                       + self.data_section_length
                                       + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
                                       ]
        tool_result, self.data_section_checksum = fi_comm_tool.array_to_int(data_section_checksum_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame data section checksum error!")

        # frame tail
        frame_tail_buffer = self.data[
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                            + self.data_section_length
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM:
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                            + self.data_section_length
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
                            + CommManagerV3Frame.LENGTH_OF_FRAME_TAIL
                            ]
        tool_result, self.frame_tail = fi_comm_tool.array_to_int(frame_tail_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_data frame tail error!")

    def update_from_parameters(self):
        self.data = []

        # frame header
        self.data.extend(CommManagerV3Frame.FRAME_HEADER_BUFFER)

        # protocol version
        tool_result, protocol_version_buffer = fi_comm_tool.int_to_array(
            self.protocol_version, size=CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data.extend(protocol_version_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        # data section length (set as 0 at start)
        self.data_section_length = 0

        tool_result, data_section_length_buffer = fi_comm_tool.int_to_array(
            self.data_section_length,
            size=CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH,
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data.extend(data_section_length_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        # data section
        self.data_section = []

        tool_result, function_type_buffer = fi_comm_tool.int_to_array(
            self.funcation_type, size=CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(function_type_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        tool_result, operation_mode_buffer = fi_comm_tool.int_to_array(
            self.operation_mode, size=CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(operation_mode_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        tool_result, read_write_buffer = fi_comm_tool.int_to_array(
            self.read_write, size=CommManagerV3Frame.LENGTH_OF_READ_WRITE
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(read_write_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        tool_result, operation_result_buffer = fi_comm_tool.int_to_array(
            self.operation_result, size=CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(operation_result_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        tool_result, parameter_type_buffer = fi_comm_tool.int_to_array(
            self.parameter_type, size=CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(parameter_type_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        tool_result, parameter_size_buffer = fi_comm_tool.int_to_array(
            self.parameter_size, size=CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data_section.extend(parameter_size_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        self.data_section.extend(self.parameters)

        self.data.extend(self.data_section)

        # data section length (set as len(self.data_section) at here)
        self.data_section_length = len(self.data_section)

        tool_result, data_section_length_buffer = fi_comm_tool.int_to_array(
            self.data_section_length,
            size=CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH,
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data[
            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION:
            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
            ] = data_section_length_buffer
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        # data section checksum
        tool_result, data_section_checksum_buffer = fi_comm_tool.int_to_array(
            self.data_section_checksum,
            size=CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM,
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data.extend(data_section_checksum_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

        # frame tail
        tool_result, frame_tail_buffer = fi_comm_tool.int_to_array(
            self.frame_tail, size=CommManagerV3Frame.LENGTH_OF_FRAME_TAIL
        )

        if tool_result == FunctionResult.SUCCESS:
            self.data.extend(frame_tail_buffer)
        else:
            Logger().print_warning("CommManagerV3Frame _update_from_parameters error!")

    def set_operation_result(self, operation_result):
        self.operation_result = operation_result

        return FunctionResult.SUCCESS

    def set_parameter_type(self, parameter_type):
        self.parameter_type = parameter_type

        # change data section length based on parameter type
        if self.parameter_type == CommParameterType.NONE:
            self.parameters = []
        elif self.parameter_type == CommParameterType.CHAR:
            if len(self.parameters < 1 * self.parameter_size):
                self.parameters.extend(numpy.zeros(1 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 1 * self.parameter_size]
        elif self.parameter_type == CommParameterType.SHORT:
            if len(self.parameters < 2 * self.parameter_size):
                self.parameters.extend(numpy.zeros(2 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 2 * self.parameter_size]
        elif self.parameter_type == CommParameterType.SHORT:
            if len(self.parameters < 4 * self.parameter_size):
                self.parameters.extend(numpy.zeros(4 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 4 * self.parameter_size]
        else:
            return FunctionResult.FAIL

        self.data_section_length = (
                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                + CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE
                + len(self.parameters)
        )

        return FunctionResult.SUCCESS

    def set_parameter_size(self, parameter_size):
        self.parameter_size = parameter_size

        # change data section length based on parameter count
        if self.parameter_type == CommParameterType.NONE:
            self.parameters = []
        elif self.parameter_type == CommParameterType.CHAR:
            if len(self.parameters < 1 * self.parameter_size):
                self.parameters.extend(numpy.zeros(1 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 1 * self.parameter_size]
        elif self.parameter_type == CommParameterType.SHORT:
            if len(self.parameters < 2 * self.parameter_size):
                self.parameters.extend(numpy.zeros(2 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 2 * self.parameter_size]
        elif self.parameter_type == CommParameterType.SHORT:
            if len(self.parameters < 4 * self.parameter_size):
                self.parameters.extend(numpy.zeros(4 * self.parameter_size - len(self.parameters)))
            else:
                self.parameters = self.parameters[: 4 * self.parameter_size]
        else:
            return FunctionResult.FAIL

        self.data_section_length = (
                CommManagerV3Frame.LENGTH_OF_FUNCTION_TYPE
                + CommManagerV3Frame.LENGTH_OF_OPERATION_MODE
                + CommManagerV3Frame.LENGTH_OF_READ_WRITE
                + CommManagerV3Frame.LENGTH_OF_OPERATION_RESULT
                + CommManagerV3Frame.LENGTH_OF_PARAMETER_TYPE
                + CommManagerV3Frame.LENGTH_OF_PARAMETER_SIZE
                + len(self.parameters)
        )

        return FunctionResult.SUCCESS

    def set_parameters(self, parameters):
        self.parameters = parameters

        self.update_from_parameters()

    def set_data_section_checksum(self, data_section_checksum):
        tool_result, data_section_checksum_buffer = fi_comm_tool.int_to_array(
            data_section_checksum, CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
        )

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        self.data[
        CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
        + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
        + self.data_section_length:
        CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
        + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
        + self.data_section_length
        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
        ] = data_section_checksum_buffer

        return FunctionResult.SUCCESS

    @staticmethod
    def check_legal(data_of_frame):
        # frame header correct?
        frame_header_buffer = data_of_frame[
                              0:
                              CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                              ]
        tool_result, frame_header = fi_comm_tool.array_to_int(frame_header_buffer)

        if tool_result == FunctionResult.SUCCESS and frame_header == CommManagerV3Frame.FRAME_HEADER:
            pass
        else:
            return FunctionResult.FAIL

        # length correct?
        data_section_length_buffer = data_of_frame[
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION:
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                     + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                                     ]
        tool_result, data_section_length = fi_comm_tool.array_to_int(data_section_length_buffer)

        if tool_result == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        data_estimate_length = (
                CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                + data_section_length
                + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
                + CommManagerV3Frame.LENGTH_OF_FRAME_TAIL
        )

        if len(data_of_frame) == data_estimate_length:
            pass
        else:
            return FunctionResult.FAIL

        # data section checksum correct?

        # frame tail correct?
        frame_tail_buffer = data_of_frame[
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                            + data_section_length
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM:
                            CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                            + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                            + data_section_length
                            + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
                            + CommManagerV3Frame.LENGTH_OF_FRAME_TAIL
                            ]

        tool_result, frame_tail = fi_comm_tool.array_to_int(frame_tail_buffer)

        if tool_result == FunctionResult.SUCCESS and frame_tail == CommManagerV3Frame.FRAME_TAIL:
            pass
        else:
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    @staticmethod
    def calculate_checksum(data_of_frame):
        data_section_length_buffer = data_of_frame[
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION:
                                     CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                                     + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                                     + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                                     ]
        tool_result, data_section_length = fi_comm_tool.array_to_int(data_section_length_buffer)

        data_section = data_of_frame[
                       CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                       + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                       + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH:
                       CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                       + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                       + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                       + data_section_length
                       ]

        data_section_checksum = 0
        for i in range(len(data_section)):
            data_section_checksum += data_section[i]
        data_section_checksum = data_section_checksum & 0xFF

        return data_section_checksum
