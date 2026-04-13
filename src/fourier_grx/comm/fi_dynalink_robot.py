from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.comm.fi_dynalink_base import DynalinkBase


class DynalinkRobot(DynalinkBase):
    """
    Dynalink Robot 模块，用于机器人模块的数据交互[单例模式]
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def _create_components(self):
        # --------------------------------------------
        # sensor information 传感器信息
        self.sensor_imus_quat_value: list = []
        self.sensor_imus_euler_angle_value: list = []
        self.sensor_imus_angular_velocity_value: list = []
        self.sensor_imus_linear_acceleration_value: list = []

        # --------------------------------------------
        # actuator information 执行器信息
        self.flag_actuator_installed: list = []
        self.flag_actuator_accessible: list = []
        self.flag_actuator_enables: list = []
        self.flag_actuator_error: list = []

        self.actuator_measured_control_mode: list = []
        self.actuator_measured_position: list = []
        self.actuator_measured_velocity: list = []
        self.actuator_measured_acceleration: list = []
        self.actuator_measured_effort: list = []
        self.actuator_measured_current: list = []

        self.actuator_output_control_mode: list = []
        self.actuator_output_position: list = []
        self.actuator_output_velocity: list = []
        self.actuator_output_acceleration: list = []
        self.actuator_output_effort: list = []
        self.actuator_output_current: list = []

        # --------------------------------------------
        # joint information 关节信息
        self.joint_mode_of_operation: list = []
        self.joint_control_word: list = []
        self.joint_status_word: list = []

        self.joint_application_position: list = []
        self.joint_application_velocity: list = []
        self.joint_application_effort: list = []

        self.joint_measured_control_mode: list = []
        self.joint_measured_position: list = []
        self.joint_measured_velocity: list = []
        self.joint_measured_acceleration: list = []
        self.joint_measured_effort: list = []
        self.joint_measured_current: list = []

        self.joint_output_control_mode: list = []
        self.joint_output_position: list = []
        self.joint_output_velocity: list = []
        self.joint_output_acceleration: list = []
        self.joint_output_effort: list = []
        self.joint_output_current: list = []

        # --------------------------------------------
        # end effector information 末端信息
        self.end_effector_measured_position: list = []
        self.end_effector_measured_velocity: list = []
        self.end_effector_measured_acceleration: list = []
        self.end_effector_measured_effort: list = []

        # --------------------------------------------
        # robot information 机器人信息
        self.flag_robot_self_check = FlagState.CLEAR
        self.flag_robot_calibration = FlagState.CLEAR
        self.flag_robot_servo_on = FlagState.CLEAR
        self.flag_robot_emergent_stop = FlagState.CLEAR
        self.flag_robot_fault = FlagState.CLEAR
        self.flag_robot_error = FlagState.CLEAR
        self.flag_robot_pinched = FlagState.CLEAR
        self.flag_robot_over_load = FlagState.CLEAR
        self.flag_robot_torque_protection = FlagState.CLEAR

        self.clear_flag_robot_over_load = FlagState.CLEAR
        self.clear_flag_robot_torque_protection = FlagState.CLEAR

        self.robot_name = ""
        self.robot_work_space = 0

        # --------------------------------------------------

        # 定义可读字段列表
        self.read_fields = [
            # --------------------------------------------
            # sensor information 传感器信息
            "sensor_imus_quat_value",
            "sensor_imus_euler_angle_value",
            "sensor_imus_angular_velocity_value",
            "sensor_imus_linear_acceleration_value",

            # --------------------------------------------
            # actuator information 执行器信息
            "flag_actuator_installed",
            "flag_actuator_accessible",
            "flag_actuator_enables",
            "flag_actuator_error",

            "actuator_measured_control_mode",
            "actuator_measured_position",
            "actuator_measured_velocity",
            "actuator_measured_acceleration",
            "actuator_measured_effort",
            "actuator_measured_current",

            "actuator_output_control_mode",
            "actuator_output_position",
            "actuator_output_velocity",
            "actuator_output_acceleration",
            "actuator_output_effort",
            "actuator_output_current",

            # --------------------------------------------
            # joint information 关节信息
            "joint_mode_of_operation",
            "joint_control_word",
            "joint_status_word",

            "joint_application_position",
            "joint_application_velocity",
            "joint_application_effort",

            "joint_measured_control_mode",
            "joint_measured_position",
            "joint_measured_velocity",
            "joint_measured_acceleration",
            "joint_measured_effort",
            "joint_measured_current",

            "joint_output_control_mode",
            "joint_output_position",
            "joint_output_velocity",
            "joint_output_acceleration",
            "joint_output_effort",
            "joint_output_current",

            # --------------------------------------------
            # end effector information 末端信息
            "end_effector_measured_position",
            "end_effector_measured_velocity",
            "end_effector_measured_acceleration",
            "end_effector_measured_effort",

            # --------------------------------------------
            # robot information 机器人信息
            "flag_robot_self_check",
            "flag_robot_calibration",
            "flag_robot_servo_on",
            "flag_robot_emergent_stop",
            "flag_robot_fault",
            "flag_robot_error",
            "flag_robot_pinched",
            "flag_robot_over_load",
            "flag_robot_torque_protection",

            "robot_name",
            "robot_work_space",
        ]

        # 定义可写字段列表
        self.write_fields = [
            "clear_flag_robot_over_load",
            "clear_flag_robot_torque_protection",
        ]

        # 合并所有字段
        self.dict_fields = self.read_fields + self.write_fields

    def init(self, **kwargs) -> FunctionResult:
        robot = kwargs.get("robot", None)

        Logger().print_info(
            f"DynalinkRobot init with robot: {robot.__class__.__name__ if robot else 'None'}"
        )

        if robot is not None:
            # --------------------------------------------
            # robot information 机器人信息
            self.robot_name = robot.robot_name
            self.robot_work_space = robot.work_space

        return FunctionResult.SUCCESS
