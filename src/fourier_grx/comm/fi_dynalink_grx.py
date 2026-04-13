from typing import Any, List
from fourier_grx.comm.fi_dynalink_base import (
    DynalinkBase
)


class DynalinkGRX(DynalinkBase):
    """
    Dynalink GRX 模块，用于 GRX 模块的数据交互[单例模式]
    
    该模块负责处理与 GRX 模块相关的所有数据交互，包括：
    1. 机器人状态信息（错误码、电池状态等）
    2. 虚拟设备控制器指令
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> 'DynalinkGRX':
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._create_components()
        return cls._instance

    def _create_components(self) -> None:
        # 版本信息
        self.fourier_core_version = ""
        self.fourier_grx_version = ""

        # 机器人状态信息
        self.robot_error_codes: List[int] = []  # 机器人错误码列表
        self.robot_battery_percentage: float = 0.0  # 电池电量百分比 0.0-1.0
        self.robot_charging_level: int = 0  # 电池电量等级 1-3
        self.robot_charging_state: float = 0.0  # 电池充电状态 0.0:未充电 1.0:充电中

        """
        Jason 2024-11-27:
        这里使用虚拟外设的定义，本质上是一种设计思想的问题。
        1. 从功能上来说，虚拟外设在 fourier-grx 的定义实际上是限定了外部对内部控制的方式。只有我们指定的接口形式，才能被外部调用。
        2. 这个设计思想是为了保证外部对内部的控制是有限制的，不会随意调用内部的接口，导致系统的不稳定。
        3. 同时，这也保证了外部在使用我们的机器人的时候，需要理解并按照我们的接口规范来调用，这样可以保证我们的系统是稳定的。
        """
        # --------------------------------------------------
        # 虚拟摇杆控制指令信息
        self.virtual_joystick_button_up: int = 0
        self.virtual_joystick_button_down: int = 0
        self.virtual_joystick_button_left: int = 0
        self.virtual_joystick_button_right: int = 0
        self.virtual_joystick_button_l1: int = 0
        self.virtual_joystick_button_l2: int = 0
        self.virtual_joystick_button_r1: int = 0
        self.virtual_joystick_button_r2: int = 0
        self.virtual_joystick_axis_left: List[float] = [0.0, 0.0]  # 左摇杆坐标 (X, Y)
        self.virtual_joystick_axis_right: List[float] = [0.0, 0.0]  # 右摇杆坐标 (X, Y)

        # --------------------------------------------------
        # 虚拟键盘控制指令信息
        self.virtual_keyboard_key_up: int = 0
        self.virtual_keyboard_key_down: int = 0
        self.virtual_keyboard_key_left: int = 0
        self.virtual_keyboard_key_right: int = 0
        self.virtual_keyboard_key_enter: int = 0
        self.virtual_keyboard_key_esc: int = 0
        self.virtual_keyboard_key_f1: int = 0
        self.virtual_keyboard_key_f2: int = 0
        self.virtual_keyboard_key_f3: int = 0
        self.virtual_keyboard_key_f4: int = 0
        self.virtual_keyboard_key_q: int = 0
        self.virtual_keyboard_key_w: int = 0
        self.virtual_keyboard_key_e: int = 0
        self.virtual_keyboard_key_a: int = 0
        self.virtual_keyboard_key_s: int = 0
        self.virtual_keyboard_key_d: int = 0

        # --------------------------------------------------
        # 虚拟鼠标控制指令信息
        self.virtual_mouse_button_left: int = 0
        self.virtual_mouse_button_right: int = 0
        self.virtual_mouse_button_middle: int = 0
        self.virtual_mouse_axis: List[float] = [0.0, 0.0]  # 鼠标坐标 (X, Y)

        # --------------------------------------------------
        # 虚拟遥操作控制器控制指令信息
        self.virtual_teleoperation_head_pose: List[float] = [0.0, 0.0, 0.0]  # 头部姿态 (roll, pitch, yaw)
        self.virtual_teleoperation_left_handle_pose: List[float] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]  # 左手姿态 (xyz, qw qx qy qz)
        self.virtual_teleoperation_right_handle_pose: List[float] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]  # 右手姿态 (xyz, qw qx qy qz)
        self.virtual_teleoperation_button_left: int = 0  # 左手按键
        self.virtual_teleoperation_button_right: int = 0  # 右手按键

        # --------------------------------------------------
        # 虚拟用户指令信息
        self.virtual_user_upper_leg_length_left: float = 0.0
        self.virtual_user_upper_leg_length_right: float = 0.0
        self.virtual_user_lower_leg_length_left: float = 0.0
        self.virtual_user_lower_leg_length_right: float = 0.0
        self.virtual_user_upper_arm_length_left: float = 0.0
        self.virtual_user_upper_arm_length_right: float = 0.0
        self.virtual_user_lower_arm_length_left: float = 0.0
        self.virtual_user_lower_arm_length_right: float = 0.0

        # 针对康复患者的关节限制参数
        self.virtual_user_knee_restriction_left: float = 0.0
        self.virtual_user_knee_restriction_right: float = 0.0

        # --------------------------------------------------
        # 虚拟面板控制指令信息
        self.virtual_panel_command_param_1: float = 0.0  # 面板参数1
        self.virtual_panel_command_param_2: float = 0.0  # 面板参数2
        self.virtual_panel_command_param_3: float = 0.0  # 面板参数3
        self.virtual_panel_command_param_4: float = 0.0  # 面板参数4
        self.virtual_panel_command_param_5: float = 0.0  # 面板参数5
        self.virtual_panel_command_param_6: float = 0.0  # 面板参数6
        self.virtual_panel_command_param_7: float = 0.0  # 面板参数7
        self.virtual_panel_command_param_8: float = 0.0  # 面板参数8
        self.virtual_panel_command_param_9: float = 0.0  # 面板参数9
        self.virtual_panel_command_switch_1: bool = False  # 面板开关1
        self.virtual_panel_command_switch_2: bool = False  # 面板开关2
        self.virtual_panel_command_switch_3: bool = False  # 面板开关3
        self.virtual_panel_command_switch_4: bool = False  # 面板开关4
        self.virtual_panel_command_switch_5: bool = False  # 面板开关5
        self.virtual_panel_command_picker_1: int = 0  # 面板选择器1
        self.virtual_panel_command_picker_2: int = 0  # 面板选择器2
        self.virtual_panel_command_picker_3: int = 0  # 面板选择器3
        self.virtual_panel_command_start: bool = False  # 启动命令
        self.virtual_panel_command_stop: bool = False  # 停止命令
        self.virtual_panel_command_pause: bool = False  # 暂停命令

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields: List[str] = [
            "fourier_core_version",
            "fourier_grx_version",

            "robot_error_codes",
            "robot_battery_percentage",
            "robot_charging_level",
            "robot_charging_state",
        ]

        # 定义可写字段列表
        self.write_fields: List[str] = [
            # --------------------------------------------------
            # 虚拟摇杆控制指令信息
            "virtual_joystick_button_up",
            "virtual_joystick_button_down",
            "virtual_joystick_button_left",
            "virtual_joystick_button_right",
            "virtual_joystick_button_l1",
            "virtual_joystick_button_l2",
            "virtual_joystick_button_r1",
            "virtual_joystick_button_r2",
            "virtual_joystick_axis_left",
            "virtual_joystick_axis_right",

            # --------------------------------------------------
            # 虚拟键盘控制指令信息
            "virtual_keyboard_key_up",
            "virtual_keyboard_key_down",
            "virtual_keyboard_key_left",
            "virtual_keyboard_key_right",
            "virtual_keyboard_key_enter",
            "virtual_keyboard_key_esc",
            "virtual_keyboard_key_f1",
            "virtual_keyboard_key_f2",
            "virtual_keyboard_key_f3",
            "virtual_keyboard_key_f4",
            "virtual_keyboard_key_q",
            "virtual_keyboard_key_w",
            "virtual_keyboard_key_e",
            "virtual_keyboard_key_a",
            "virtual_keyboard_key_s",
            "virtual_keyboard_key_d",

            # --------------------------------------------------
            # 虚拟鼠标控制指令信息
            "virtual_mouse_button_left",
            "virtual_mouse_button_right",
            "virtual_mouse_button_middle",
            "virtual_mouse_axis",

            # --------------------------------------------------
            # 虚拟遥操作控制器控制指令信息
            "virtual_teleoperation_left_handle_pose",
            "virtual_teleoperation_right_handle_pose",
            "virtual_teleoperation_head_pose",
            "virtual_teleoperation_button_left",
            "virtual_teleoperation_button_right",

            # --------------------------------------------------
            # 虚拟用户指令信息
            "virtual_user_upper_leg_length_left",
            "virtual_user_upper_leg_length_right",
            "virtual_user_lower_leg_length_left",
            "virtual_user_lower_leg_length_right",
            "virtual_user_upper_arm_length_left",
            "virtual_user_upper_arm_length_right",
            "virtual_user_lower_arm_length_left",
            "virtual_user_lower_arm_length_right",

            "virtual_user_knee_restriction_left",
            "virtual_user_knee_restriction_right",

            # --------------------------------------------------
            # 虚拟面板控制指令信息
            "virtual_panel_command_param_1",
            "virtual_panel_command_param_2",
            "virtual_panel_command_param_3",
            "virtual_panel_command_param_4",
            "virtual_panel_command_param_5",
            "virtual_panel_command_param_6",
            "virtual_panel_command_param_7",
            "virtual_panel_command_param_8",
            "virtual_panel_command_param_9",
            "virtual_panel_command_switch_1",
            "virtual_panel_command_switch_2",
            "virtual_panel_command_switch_3",
            "virtual_panel_command_switch_4",
            "virtual_panel_command_switch_5",
            "virtual_panel_command_picker_1",
            "virtual_panel_command_picker_2",
            "virtual_panel_command_picker_3",
            "virtual_panel_command_start",
            "virtual_panel_command_stop",
            "virtual_panel_command_pause",
        ]

        # 合并所有字段
        self.dict_fields: List[str] = self.read_fields + self.write_fields
