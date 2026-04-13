from typing import List

from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkCore(DynalinkBase):
    """
    Dynalink APP 模块，用于 APP 模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        # 版本信息
        self.software_version = ""

        # 序列号信息
        self.robot_serial_number = ""

        self.flag_robot_serial_number_update = FlagState.CLEAR

        # 机器人控制频率信息
        self.control_period = 1.0

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields: List[str] = [
            "software_version",
            "robot_serial_number",
            "control_period",
        ]

        # 定义可写字段列表
        self.write_fields: List[str] = [
        ]

        # 合并所有字段
        self.dict_fields = self.read_fields + self.write_fields
