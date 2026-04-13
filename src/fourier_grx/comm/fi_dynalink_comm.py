from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkComm(DynalinkBase):
    """
    Dynalink Comm 模块，用于通信模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        self.flag_heart_beat = FlagState.SET  # 心跳信号
        self.flag_ethernet_connect_status = FlagState.CLEAR  # 主机与机器人以太网连接状态

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields = [
            "flag_heart_beat",
            "flag_ethernet_connect_status",
        ]

        # 定义可写字段列表
        self.write_fields = [
        ]
        
        # 合并所有字段
        self.dict_fields = self.read_fields + self.write_fields
