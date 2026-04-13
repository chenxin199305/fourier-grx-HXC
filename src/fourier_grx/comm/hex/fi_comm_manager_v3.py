import fourier_grx.comm.hex.fi_comm_tool as fi_comm_tool
from fourier_core.predefine import *

from fourier_grx.comm.hex.fi_comm_function_type import CommFunctionType
from fourier_grx.comm.hex.fi_comm_manager_v3_frame import CommManagerV3Frame
from fourier_grx.comm.hex.fi_comm_manager_v3_hardware import CommManagerV3Hardware
from fourier_grx.comm.hex.fi_comm_manager_v3_communication import CommManagerV3Communication
from fourier_core.comm.hex.fi_comm_manager_v3_app import CommManagerV3APP


class CommManagerV3:
    ETHERNET_RECEIVE_DATA_MAX_LENGTH = 1024
    ETHERNET_SEND_DATA_MAX_LENGTH = 1024

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            cls._instance.receive_data = []
            cls._instance.send_data = []
            cls._instance.start_index_of_receive_data = 0
            cls._instance.stop_index_of_receive_data = 0
            cls._instance.offset_index_of_receive_data = 0

            cls._instance.receive_frame: CommManagerV3Frame = CommManagerV3Frame()
            cls._instance.send_frame: CommManagerV3Frame = CommManagerV3Frame()

            cls._instance._create_sections()

        return cls._instance

    def __init__(self):
        pass

    def _create_sections(self):
        self.communication_section = CommManagerV3Communication()
        self.app_section = CommManagerV3APP()
        self.hardware_section = CommManagerV3Hardware()

    def _operation_decode(self, frame: CommManagerV3Frame = None):
        if frame is None:
            pass
        else:
            self.receive_frame = frame

        # deal with function and operation_mode
        response_frame = None

        if self.receive_frame.funcation_type == CommFunctionType.NONE:
            pass
        elif self.receive_frame.funcation_type == CommFunctionType.COMMUNICATION:
            response_frame = self.communication_section.decode(self.receive_frame)
        elif self.receive_frame.funcation_type == CommFunctionType.APP:
            response_frame = self.app_section.decode(self.receive_frame)
        elif self.receive_frame.funcation_type == CommFunctionType.HARDWARE:
            response_frame = self.hardware_section.decode(self.receive_frame)
        else:
            pass

        return response_frame

    def _operation_encode(self, frame: CommManagerV3Frame = None):
        if frame is None:
            pass
        else:
            self.send_frame = frame

        # checksum
        data_section_checksum = CommManagerV3Frame.calculate_checksum(self.send_frame.data)
        self.send_frame.set_data_section_checksum(data_section_checksum)

        return self.send_frame

    def receive(self, data):
        self.receive_data = data

        self.start_index_of_receive_data = 0
        self.stop_index_of_receive_data = 0
        self.offset_index_of_receive_data = 0

        while self.offset_index_of_receive_data < len(self.receive_data):

            # frame header
            tool_result, self.start_index_of_receive_data = \
                fi_comm_tool.array_find(
                    self.receive_data,
                    CommManagerV3Frame.FRAME_HEADER_BUFFER,
                    start_index=self.offset_index_of_receive_data,
                )

            if tool_result == FunctionResult.SUCCESS:
                pass
            else:
                break

            # data section
            data_section_length_buffer = \
                self.receive_data[
                self.start_index_of_receive_data
                + CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION:
                self.start_index_of_receive_data
                + CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                ]

            tool_result, data_section_length = fi_comm_tool.array_to_int(data_section_length_buffer)

            if tool_result == FunctionResult.SUCCESS:
                pass
            else:
                self.offset_index_of_receive_data += 1
                continue

            # check size
            if self.start_index_of_receive_data >= 0:
                self.stop_index_of_receive_data = (
                        self.start_index_of_receive_data
                        + CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                        + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                        + data_section_length
                        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_CHECKSUM
                )
            else:
                self.offset_index_of_receive_data += 1
                continue

            if self.stop_index_of_receive_data > len(self.receive_data):
                self.offset_index_of_receive_data += 1
                continue

            # check frame tail
            if self.receive_data[self.stop_index_of_receive_data] == CommManagerV3Frame.FRAME_TAIL:
                pass
            else:
                self.offset_index_of_receive_data += 1
                continue

            # check checksum
            checksum_buffer = []
            for i in range(data_section_length):
                checksum_buffer.append(
                    self.receive_data[
                        self.start_index_of_receive_data
                        + CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                        + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                        + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                        + i
                        ]
                )

            checksum = 0
            for i in range(len(checksum_buffer)):
                checksum += checksum_buffer[i]
            checksum = checksum & 0xFF

            if (
                    checksum
                    == self.receive_data[
                self.start_index_of_receive_data
                + CommManagerV3Frame.LENGTH_OF_FRAME_HEADER
                + CommManagerV3Frame.LENGTH_OF_PROTOCOL_VERSION
                + CommManagerV3Frame.LENGTH_OF_DATA_SECTION_LENGTH
                + data_section_length
            ]
            ):
                pass
            else:
                self.offset_index_of_receive_data += 1
                continue

            # frame
            frame_buffer = []
            frame_length = self.stop_index_of_receive_data - self.start_index_of_receive_data + 1
            for i in range(frame_length):
                frame_buffer.append(self.receive_data[self.start_index_of_receive_data + i])

            self.receive_frame = CommManagerV3Frame(frame_buffer)

            # operation_mode decode
            response_frame = self._operation_decode(self.receive_frame)

            # operation_mode encode
            self.send_frame = self._operation_encode(response_frame)

            # send response frame
            self.send(self.send_frame.data)

            # moving offset index + len(frame) or next frame start
            self.offset_index_of_receive_data = self.stop_index_of_receive_data

        # finish, clear receive_data
        self.receive_data = []

    def send(self, data):
        # 说明：send() 主要负责将要发送的数据帧统一汇总到 self.send_data，具体的发送由外部操作完成
        self.send_data.extend(data)
        # print("CommManagerV3 self.send_data self.send_data = ", self.send_data)

    def set_receive_data(self, data):
        self.receive_data = data

    def set_send_data(self, data):
        self.send_data = data

    def clear_receive_data(self):
        self.receive_data = []

    def clear_send_data(self):
        self.send_data = []
