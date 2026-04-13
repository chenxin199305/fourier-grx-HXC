from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkTask(DynalinkBase):
    """
    Dynalink FSMItem 模块，用于任务模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        # --------------------------------------------------
        # 任务控制指令信息
        self.flag_task_command_update: int = FlagState.CLEAR
        self.flag_task_start: int = FlagState.CLEAR
        self.flag_task_running: int = FlagState.CLEAR
        self.flag_task_finish: int = FlagState.CLEAR
        self.flag_task_pause: int = FlagState.CLEAR

        self.robot_task_command: int = 0  # 任务指令
        self.robot_task_state: int = 0  # 任务状态
        self.robot_task_command_data: dict = {}  # 任务指令数据 (不同任务不同数值)
        self.robot_task_state_data: dict = {}  # 任务状态数据 (不同任务不同数值)

        # 模块控制指令信息
        self.flag_component_command_update: int = FlagState.CLEAR
        self.flag_component_start: int = FlagState.CLEAR
        self.flag_component_in_process: int = FlagState.CLEAR
        self.flag_component_finish: int = FlagState.CLEAR

        self.robot_component_command: int = 0  # 模块指令
        self.robot_component_state: int = 0  # 模块状态
        self.robot_component_command_data: dict = {}  # 模块指令数据 (不同任务不同数值)
        self.robot_component_state_data: dict = {}  # 模块状态数据 (不同任务不同数值)

        # --------------------------------------------------

        self.read_fields = [
            # --------------------------------------------------
            # 任务状态信息
            "flag_task_start",
            "flag_task_running",
            "flag_task_finish",
            "flag_task_pause",

            "robot_task_state",
            "robot_task_state_data",

            # --------------------------------------------------
            # 模块状态信息
            "flag_component_start",
            "flag_component_in_process",
            "flag_component_finish",

            "robot_component_state",
            "robot_component_state_data",
        ]
        self.write_fields = [
            # --------------------------------------------------
            # 任务控制指令信息
            "flag_task_command_update",
            "robot_task_command",
            "robot_task_command_data",

            # --------------------------------------------------
            # 模块控制指令信息
            "flag_component_command_update",
            "robot_component_command",
            "robot_component_command_data",
        ]
        self.dict_fields = self.read_fields + self.write_fields
