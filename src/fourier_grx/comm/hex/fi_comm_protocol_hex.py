from fourier_core.logger import *
from fourier_core.predefine import *

import fourier_grx.comm.hex.fi_comm_tool as fi_comm_tool
from fourier_grx.comm.hex.fi_comm_manager_v3_frame import CommManagerV3Frame


class CommProtocolHex:
    RECEIVE_DATA_MAX_LENGTH = 1024
    REMAIN_DATA_MAX_LENGTH = 1024
    EXPLAIN_DATA_MAX_LENGTH = 2048
    SEND_DATA_MAX_LENGTH = 2048

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            cls.parse_type: str = "server"

            cls.receive_data = []  # 收到的数据
            cls.remain_data = []  # 余留数据（用于与下一个 receive_data 汇总）
            cls.explain_data = []  # 待解析的数据（抽离出每一个完整帧）
            cls.send_data = []  # 待发送的数据

        return cls._instance

    def __init__(self, dynalink_interface=None):
        if dynalink_interface is None:
            if hasattr(self, "dynalink_interface"):
                pass
            else:
                from fourier_grx.comm.fi_dynalink_manager import DynalinkManager
                self.dynalink_interface = DynalinkManager()
        else:
            self.dynalink_interface = dynalink_interface

    def set_parse_type(self, parse_type: str):
        if parse_type not in ["server", "client"]:
            Logger().print_error("CommProtocolJson set_parse_type unknown parse_type!")
            return FunctionResult.FAIL

        self.parse_type = parse_type

    def receive(self, data):
        self.receive_data = data

        # Logger().print_debug(f"CommProtocolHex receive_data: {self.receive_data}")

        self._parse()

    def send(self, data):
        self.send_data.extend(data)

        # Logger().print_debug(f"CommProtocolHex send_data: {self.send_data}")

    def _parse(self):
        if self.parse_type == "server":
            self._server()
        elif self.parse_type == "client":
            self._client()
        else:
            pass

    # ---------------------------------- server ----------------------------------

    def _server(self):
        # 说明：判断 receive_data 中是否有完整数据帧
        if len(self.receive_data) > 0:

            for i in range(len(self.receive_data) - 4, -1, -1):
                # find frame header
                tool_result, frame_header = fi_comm_tool.array_to_int(self.receive_data[i: i + 4])

                if tool_result == FunctionResult.SUCCESS and frame_header == CommManagerV3Frame.FRAME_HEADER:
                    if i > 0:
                        if (self.receive_data[i - 1]) == CommManagerV3Frame.FRAME_TAIL:
                            # 说明：至少凑够1帧数据，才放于 explain_data
                            self.explain_data.extend(self.remain_data)  # copy remain_data -> explain data
                            self.explain_data.extend(self.receive_data[:i])
                            # 说明：检测余下数据是否构成1帧
                            if CommManagerV3Frame.check_legal(self.receive_data[i:]) == FunctionResult.SUCCESS:
                                self.explain_data.extend(self.receive_data[i:])
                            else:
                                # copy receive_data -> remain_data，余半帧数据在 remain_data
                                self.remain_data = []
                                self.remain_data.extend(self.receive_data[i:])
                            break  # 退出循环
                        else:
                            pass
                    elif i == 0:
                        # 说明：至少凑够1帧数据，才放于 explain_data
                        self.explain_data.extend(self.remain_data)  # copy remain_data -> explain data
                        self.explain_data.extend(self.receive_data[:i])
                        # 说明：检测余下数据是否构成1帧
                        if CommManagerV3Frame.check_legal(self.receive_data[i:]) == FunctionResult.SUCCESS:
                            self.explain_data.extend(self.receive_data[i:])
                        else:
                            # copy receive_data -> remain_data，余半帧数据在 remain_data
                            self.remain_data = []
                            self.remain_data.extend(self.receive_data[i:])
                        break  # 退出循环
                    else:
                        pass

                # not find frame header
                if i == 0:
                    # 说明：没有发现1帧完整的数据，则先将数据拷贝至 remain_data <- 应对数据分段传输的问题
                    # 注意：如果一直都是这种分段的数据传输，则数据可能会积攒在 remain_data 中
                    self.remain_data.extend(self.receive_data[i:])  # copy receive_data -> remain_data
                    break
                else:
                    pass

        # 说明：判断 remain_data 中是否有完整数据帧
        if len(self.remain_data) > 0:

            for i in range(len(self.remain_data) - 4, -1, -1):
                # find frame header
                tool_result, frame_header = fi_comm_tool.array_to_int(self.remain_data[i: i + 4])

                if tool_result == FunctionResult.SUCCESS and frame_header == CommManagerV3Frame.FRAME_HEADER:
                    if i > 0:
                        if (self.remain_data[i - 1]) == CommManagerV3Frame.FRAME_TAIL:
                            self.explain_data.extend(self.remain_data[:i])
                            self.remain_data = self.remain_data[i:]  # 移除头部i个数据
                            break
                        else:
                            pass
                    elif i == 0:
                        # 说明：检测余下数据是否构成1帧
                        if CommManagerV3Frame.check_legal(self.remain_data[i:]) == FunctionResult.SUCCESS:
                            self.explain_data.extend(self.remain_data[i:])
                            self.remain_data = self.remain_data[i:]  # 移除头部i个数据
                            break
                        else:
                            pass
                        break

            # too many data in remain_data
            if len(self.remain_data) > CommProtocolHex.REMAIN_DATA_MAX_LENGTH:
                self.explain_data.extend(self.remain_data)
                self.remain_data = []

    # ---------------------------------- server ----------------------------------

    # ---------------------------------- client ----------------------------------

    def _client(self):
        pass

    # ---------------------------------- client ----------------------------------

    def set_receive_data(self, data):
        self.receive_data = data

    def set_send_data(self, data):
        self.send_data = data
        Logger().print_debug(f"CommProtocolHex set_send_data = {self.send_data}")

    def clear_receive_data(self):
        self.receive_data = []

    def clear_send_data(self):
        self.send_data = []

    def clear_explain_data(self):
        self.explain_data = []

    def clear_remain_date(self):
        self.remain_data = []
