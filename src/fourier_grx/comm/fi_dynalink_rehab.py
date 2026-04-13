from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkRehab(DynalinkBase):
    """
    Dynalink Rehab 模块，用于任务模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        # --------------------------------------------
        # joint information 关节信息
        self.reference_joint_position: list = []  # 关节参考位置 (当前时刻), rad or m
        self.reference_joint_velocity: list = []  # 关节参考速度 (当前时刻), rad/s or m/s

        self.reference_joint_position_max: list = []  # 关节参考最大位置 (轨迹全程), rad or m
        self.reference_joint_position_min: list = []  # 关节参考最小位置 (轨迹全程), rad or m

        # --------------------------------------------
        # task information 任务信息
        self.motion_ratio: float = 0  # 任务运动执行进度情况

        # --------------------------------------------------

        self.read_fields = [
            # --------------------------------------------
            # joint information 关节信息
            "reference_joint_position",
            "reference_joint_velocity",

            "reference_joint_position_max",
            "reference_joint_position_min",

            # --------------------------------------------
            # task information 任务信息
            "motion_ratio",
        ]
        self.write_fields = [
        ]
        self.dict_fields = self.read_fields + self.write_fields
