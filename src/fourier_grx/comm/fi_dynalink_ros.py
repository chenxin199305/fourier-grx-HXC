from fourier_grx.comm.fi_dynalink_base import (
    DynalinkBase
)


class DynalinkROS(DynalinkBase):
    """
    Dynalink ROS 模块，用于 ROS 模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        # --------------------------------------------
        # 高程图信息 (1m x 1m : 11 x 11 的数据数组)
        self.elevation_map: list = []

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields = [
        ]

        # 定义可写字段列表
        self.write_fields = [
            # --------------------------------------------
            # 高程图信息
            "elevation_map",
        ]

        # 合并所有字段
        self.dict_fields = self.read_fields + self.write_fields
