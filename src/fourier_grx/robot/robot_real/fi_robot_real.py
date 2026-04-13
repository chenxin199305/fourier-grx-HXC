import os
import sys
import time
import numpy
import json
import yaml
import zenoh
import msgpack

from fourier_core.config.fi_config import gl_config
from fourier_core.config.zenoh_config import gl_zenoh_config
from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.actuator import ActuatorBase, ActuatorMotor
from fourier_core.joint import JointBase

from fourier_grx.predefine import *
from fourier_grx.peripheral import *

from fourier_grx.task import *
from fourier_grx.task.robot_real import *  # import all tasks, for registration
from fourier_grx.task.fi_task_registry import TaskRegistry

from fourier_grx.robot.robot_base import RobotBase


class RobotReal(RobotBase):
    """
    General Robotics (GR) Robot Real
    针对 Fourier Intelligence 机器人进行定制化开发，包括 RL 功能开发提供的基础类
    """

    def __init__(self):
        super().__init__()

        # sensor
        self.number_of_sensor_usb_imu = 0
        self.sensor_usb_imus = []
        self.sensor_usb_imu_group = None

        # ioboard
        self.number_of_ioboard = 0
        self.ioboards: list[ActuatorBase] = []
        self.ioboard_group = None

        # actuator
        self.number_of_actuator = 0
        self.actuators: list[ActuatorMotor] = []
        self.actuator_group = None

        # joint
        self.number_of_joint = 0
        self.joints: list[JointBase] = []
        self.joint_group = None

        self.joints_direction = numpy.array([])
        self.joint_home_position = numpy.array([])
        self.joint_min_position = numpy.array([])
        self.joint_max_position = numpy.array([])
        self.joints_reduction_ratio = numpy.array([])
        self.joint_kinematic_reduction_ratio = numpy.array([])
        self.joint_kinetic_reduction_ratio = numpy.array([])

        self.joint_control_mode = numpy.array([])
        self.joint_position_control_kp = numpy.array([])
        self.joint_velocity_control_kp = numpy.array([])
        self.joint_velocity_control_ki = numpy.array([])
        self.joint_pd_control_kp = numpy.array([])
        self.joint_pd_control_kd = numpy.array([])

        # end effector
        self.number_of_end_effector = 0
        self.end_effectors = []
        self.end_effector_group = None

        # robot
        self.robot_name = RobotName.Real

        # control algorithm
        # ...

        # task
        RobotReal._init_task(self)

        # communication
        self.zenoh_session = None
        self.zenoh_prefix = None
        self.zenoh_root = None
        self.zenoh_suffix = None
        self.zenoh_keys = None
        self.zenoh_key_exprs = None

        self._zenoh_publishers: dict[str, zenoh.Publisher] = {}
        self._zenoh_subscribers: dict[str, zenoh.Subscriber] = {}
        self._zenoh_services: dict[str, zenoh.Queryable] = {}

    # =====================================================================================================

    def _init_task(self) -> FunctionResult:
        """
        初始化任务管理器和任务菜单。
        """

        for task_cls in TaskRegistry.get_tasks(RobotName.Real):
            self._register_task(task_cls)

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 具体实现层函数 (创建)

    def _create_component(self) -> FunctionResult:
        """
        创建机器人组件，包括传感器、执行器、IO 板等。
        """
        return FunctionResult.SUCCESS

    def _create_buffer(self) -> FunctionResult:
        """
        创建数据缓冲区，主要用于存储传感器数据、执行器数据等。
        """

        # --------------------------------------------------
        # RobotClass
        # sensor (usb_imu)
        self.sensor_usb_imu_group_measured_quat = numpy.zeros(self.number_of_sensor_usb_imu * 4)
        self.sensor_usb_imu_group_measured_angle = numpy.zeros(self.number_of_sensor_usb_imu * 3)
        self.sensor_usb_imu_group_measured_angular_velocity = numpy.zeros(self.number_of_sensor_usb_imu * 3)
        self.sensor_usb_imu_group_measured_linear_acceleration = numpy.zeros(self.number_of_sensor_usb_imu * 3)

        # sensor (imu)
        self.number_of_sensor_imu += self.number_of_sensor_usb_imu
        self.number_of_sensor_imu += self.number_of_sensor_can_imu

        self.sensor_imu_group_measured_quat = numpy.array([0.0, 0.0, 0.0, 1.0] * self.number_of_sensor_imu)
        self.sensor_imu_group_measured_euler_angle = numpy.array([0.0, 0.0, 0.0] * self.number_of_sensor_imu)
        self.sensor_imu_group_measured_angular_velocity = numpy.array([0.0, 0.0, 0.0] * self.number_of_sensor_imu)
        self.sensor_imu_group_measured_linear_acceleration = numpy.array([0.0, 0.0, 0.0] * self.number_of_sensor_imu)

        # actuator
        self.actuator_group_measured_position = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_measured_velocity = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_measured_effort = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_measured_current = numpy.array([0.0] * self.number_of_actuator)

        self.actuator_group_target_position = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_target_velocity = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_target_effort = numpy.array([0.0] * self.number_of_actuator)
        self.actuator_group_target_current = numpy.array([0.0] * self.number_of_actuator)

        # joint
        self.joint_group_application_position = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_application_velocity = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_application_effort = numpy.array([0.0] * self.number_of_joint)

        self.joint_group_measured_position = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_measured_velocity = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_measured_effort = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_measured_current = numpy.array([0.0] * self.number_of_joint)

        self.joint_group_target_position = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_target_velocity = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_target_effort = numpy.array([0.0] * self.number_of_joint)
        self.joint_group_target_current = numpy.array([0.0] * self.number_of_joint)

        self.joint_urdf_group_measured_position = numpy.array([0.0] * self.number_of_joint)
        self.joint_urdf_group_measured_velocity = numpy.array([0.0] * self.number_of_joint)
        self.joint_urdf_group_measured_effort = numpy.array([0.0] * self.number_of_joint)

        # end effector
        self.end_effector_group_posture = numpy.array([0.0] * 6 * self.number_of_end_effector)

        self.end_effector_group_measured_position = numpy.array([[0.0] * 6] * self.number_of_end_effector)
        self.end_effector_group_measured_velocity = numpy.array([[0.0] * 6] * self.number_of_end_effector)
        self.end_effector_group_measured_effort = numpy.array([[0.0] * 6] * self.number_of_end_effector)

        self.end_effector_group_target_position = numpy.array([[0.0] * 6] * self.number_of_end_effector)
        self.end_effector_group_target_velocity = numpy.array([[0.0] * 6] * self.number_of_end_effector)
        self.end_effector_group_target_effort = numpy.array([[0.0] * 6] * self.number_of_end_effector)

        # --------------------------------------------------
        # Share (for developer)
        # sensor
        self.share_sensor_imu_group_measured_quat = numpy.zeros_like(self.sensor_imu_group_measured_quat)
        self.share_sensor_imu_group_measured_angle = numpy.zeros_like(self.sensor_imu_group_measured_euler_angle)
        self.share_sensor_imu_group_measured_angular_velocity = numpy.zeros_like(self.sensor_imu_group_measured_angular_velocity)
        self.share_sensor_imu_group_measured_linear_acceleration = numpy.zeros_like(self.sensor_imu_group_measured_linear_acceleration)

        # joint (replace by joint_urdf)
        self.share_joint_urdf_group_measured_position = numpy.zeros_like(self.joint_urdf_group_measured_position)
        self.share_joint_urdf_group_measured_velocity = numpy.zeros_like(self.joint_urdf_group_measured_velocity)
        self.share_joint_urdf_group_measured_effort = numpy.zeros_like(self.joint_urdf_group_measured_effort)

        self.share_joint_group_measured_current = numpy.zeros_like(self.actuator_group_measured_current)

        # end effector
        self.share_end_effector_group_measured_position = numpy.zeros_like(self.end_effector_group_measured_position)
        self.share_end_effector_group_measured_velocity = numpy.zeros_like(self.end_effector_group_measured_velocity)
        self.share_end_effector_group_measured_effort = numpy.zeros_like(self.end_effector_group_measured_effort)

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 具体实现层函数 (初始化)

    def _init(self) -> FunctionResult:
        """
        初始化机器人硬件平台，完成所有传感器和执行器的初始化。

        1. 初始化传感器 (USB_IMU)
            1.1 授权 USB 权限
            1.2 初始化传感器
            1.3 传感器通信使能
        2. 初始化传感器 (FI_FSE)
            2.1 初始化传感器
            2.2 传感器通信使能
        3. 初始化执行器 (FI_FSA)
            3.1 初始化执行器
            3.2 执行器通信使能
        """

        # Sensor
        # sensor_usb_imu
        for i in range(self.number_of_sensor_usb_imu):
            if self.sensor_usb_imus[i] is not None:
                function_result = self.sensor_usb_imus[i].init()

                if function_result != FunctionResult.SUCCESS:
                    Logger().print_error("Sensor USB IMU init failed!")
                    sys.exit(FunctionResult.FAIL)

        for i in range(self.number_of_sensor_usb_imu):
            try:
                comm_enable = gl_config.parameters.get("sensor_usb_imu", {}).get("comm_enable", [])[i]
            except Exception as e:
                comm_enable = True  # Default: True

            try:
                comm_frequency = gl_config.parameters.get("sensor_usb_imu", {}).get("comm_frequency", [])[i]
            except Exception as e:
                comm_frequency = 500  # Default: 500Hz

            if self.sensor_usb_imus[i] is not None:
                self.sensor_usb_imus[i].comm(enable=comm_enable, frequency=comm_frequency, )

        # sensor_fi_fse
        for i in range(self.number_of_sensor_fi_fse):
            if self.sensor_fi_fse[i] is not None:
                function_result = self.sensor_fi_fse[i].init()

                if function_result != FunctionResult.SUCCESS:
                    Logger().print_error("Sensor FI FSE init failed!")
                    sys.exit(FunctionResult.FAIL)

        for i in range(self.number_of_sensor_fi_fse):
            try:
                comm_enable = gl_config.parameters.get("sensor_fi_fse", {}).get("comm_enable", [])[i]
            except Exception as e:
                comm_enable = True  # Default: True

            try:
                use_fast = gl_config.parameters.get("sensor_fi_fse", {}).get("comm_use_fast", [])[i]
            except Exception as e:
                use_fast = False  # Default: False

            if self.sensor_fi_fse[i] is not None:
                self.sensor_fi_fse[i].comm(enable=comm_enable, use_fast=use_fast)

        # Actuator IO (ioboard)
        for i in range(self.number_of_ioboard):
            if self.ioboards[i] is not None:
                self.ioboards[i].init()

        for i in range(self.number_of_ioboard):
            if self.ioboards[i] is not None:
                self.ioboards[i].comm(enable=True)

        # Actuator
        for i in range(self.number_of_actuator):
            if self.actuators[i] is not None:
                function_result = self.actuators[i].init()

                if function_result != FunctionResult.SUCCESS:
                    Logger().print_error("Actuator init failed!")
                    sys.exit(FunctionResult.FAIL)

        for i in range(self.number_of_actuator):
            try:
                comm_enable = gl_config.parameters.get("actuator", {}).get("comm_enable", [])[i]
            except Exception as e:
                comm_enable = True  # Default: True

            try:
                use_fast = gl_config.parameters.get("actuator", {}).get("comm_use_fast", [])[i]
            except Exception as e:
                use_fast = True  # Default: True

            actuator = self.actuators[i]
            if actuator is not None:
                actuator.comm(enable=comm_enable, use_fast=use_fast)

        Logger().print_info(
            # f"{self.__class__.__name__} init() download joint PID..."
            f"{self.__class__.__name__} init() download joint PD..."
        )

        retry_count = 0
        retry_max = 5

        for i in range(self.number_of_joint):
            retry_count = 0
            result = FunctionResult.FAIL

            while result == FunctionResult.FAIL:
                if self.joints[i] is not None:
                    joint: JointBase = self.joints[i]

                    """
                    Jason 2025-12-20:
                    从默认使用 PID Position 控制模式，修改为 PD 控制模式
                    """
                    result = joint.download_control_pid(
                        # assign_control_mode=JointControlMode.POSITION,
                        assign_control_mode=JointControlMode.PD,
                        pass_repeat=False
                    )
                else:
                    break

                retry_count += 1

                if retry_count >= retry_max:
                    Logger().print_error("Robot initialize fail!")
                    Logger().print_error(f"{self.joints[i].actuator.id} has no response!")
                    sys.exit(FunctionResult.FAIL)

        # wait response all received for mode
        time.sleep(1)

        Logger().print_info("PID setup OK!")

        return FunctionResult.SUCCESS

    def _ready_state(self) -> FunctionResult:
        """
        准备状态，切换到 Real Robot FSMItem。
        """
        super()._ready_state()

        return FunctionResult.SUCCESS

    def _prepare_pub_sub_interface(self) -> FunctionResult:
        """
        准备发布订阅接口，主要用于数据的发布和订阅。
        """

        # 构建 Zenoh 节点
        self.zenoh_session = zenoh.open(gl_zenoh_config.get_config())
        self.zenoh_prefix = "fourier-grx"
        self.zenoh_root = ""
        self.zenoh_suffix = ""
        self.zenoh_keys = ["robot", "task"]
        self.zenoh_key_exprs = {}

        # 构建发布者、订阅者和服务
        for key in self.zenoh_keys:
            key_expr_core = (
                    (f"{self.zenoh_prefix}{self.zenoh_root}{self.zenoh_suffix}") +
                    (f"/{key}" if key else "")
            )

            self._zenoh_publishers[key] = self.zenoh_session.declare_publisher(
                key_expr=f"{key_expr_core}/state",
                priority=zenoh.Priority.REAL_TIME,
                congestion_control=zenoh.CongestionControl.DROP,
            )

            self._zenoh_subscribers[key] = self.zenoh_session.declare_subscriber(
                key_expr=f"{key_expr_core}/control",
                handler=self._zenoh_subscribe_handler,
            )

        # 打印 zenoh 的信息
        self.zenoh_key_exprs = {
            "publishers": {},
            "subscribers": {},
            "services": {},
        }

        for key in self.zenoh_keys:
            self.zenoh_key_exprs["publishers"][key] = str(self._zenoh_publishers[key].key_expr)
            self.zenoh_key_exprs["subscribers"][key] = str(self._zenoh_subscribers[key].key_expr)

        Logger().print_debug("#################################")
        Logger().print_debug(
            f"{self.__class__.__name__} ZenohConfig \n"
            f"authentication: {gl_zenoh_config.authentication} \n"
            f"username: {gl_zenoh_config.username} \n"
            f"password: {gl_zenoh_config.password} \n"
            f"credentials_config_path: {gl_zenoh_config.credentials_config_path} \n"
            f"zenoh_key_exprs : \n"
            f"{json.dumps(self.zenoh_key_exprs, indent=4, ensure_ascii=False)}"
        )
        Logger().print_debug("#################################")

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 具体实现层函数 (控制循环)

    def control_loop_update_state(self) -> FunctionResult:

        # --------------------------------------------------
        # sensor
        # Note 2024-01-26:
        # no need to read fi_fse sensor in every loop
        # fi_fse
        # for i in range(self.number_of_sensor_fi_fse):
        #     self.sensor_fi_fse[i].upload()
        #
        # print("self.sensor_fi_fse = ", self.sensor_fi_fse[5].measured_angle)

        # imu
        if self.sensor_usb_imu_group is not None:
            self.sensor_usb_imu_group.upload()
        else:
            for i in range(self.number_of_sensor_usb_imu):
                self.sensor_usb_imus[i].upload()

        quat_array = numpy.array([imu.measured_quat for imu in self.sensor_usb_imus]).flatten()
        angle_array = numpy.array([imu.measured_angle for imu in self.sensor_usb_imus]).flatten()
        angular_velocity_array = numpy.array([imu.measured_angular_velocity for imu in self.sensor_usb_imus]).flatten()
        acceleration_array = numpy.array([imu.measured_acceleration for imu in self.sensor_usb_imus]).flatten()

        self.sensor_usb_imu_group_measured_quat[:] = quat_array
        self.sensor_usb_imu_group_measured_angle[:] = angle_array
        self.sensor_usb_imu_group_measured_angular_velocity[:] = angular_velocity_array
        self.sensor_usb_imu_group_measured_linear_acceleration[:] = acceleration_array

        # sensor usb_imu -> sensor imu
        self.sensor_imu_group_measured_quat = (self.sensor_usb_imu_group_measured_quat.copy())
        self.sensor_imu_group_measured_euler_angle = (self.sensor_usb_imu_group_measured_angle.copy())
        self.sensor_imu_group_measured_angular_velocity = (self.sensor_usb_imu_group_measured_angular_velocity.copy())
        self.sensor_imu_group_measured_linear_acceleration = (self.sensor_usb_imu_group_measured_linear_acceleration.copy())

        # --------------------------------------------------
        # ioboard
        if self.ioboard_group is not None:
            self.ioboard_group.upload()
        else:
            for ioboard in self.ioboards:
                ioboard.upload()

        # --------------------------------------------------
        # actuator
        if self.actuator_group is not None:
            self.actuator_group.upload()
        else:
            for actuator in self.actuators:
                actuator.upload()

        self.actuator_group_measured_position = numpy.array([actuator.measured_position for actuator in self.actuators])
        self.actuator_group_measured_velocity = numpy.array([actuator.measured_velocity for actuator in self.actuators])
        self.actuator_group_measured_effort = numpy.array([actuator.measured_effort for actuator in self.actuators])
        self.actuator_group_measured_current = numpy.array([actuator.measured_current for actuator in self.actuators])

        # --------------------------------------------------
        # joint
        if self.joint_group is not None:
            self.joint_group.update()
        else:
            for joint in self.joints:
                joint.update()

        self.joint_group_application_position = numpy.array([joint.application_position for joint in self.joints])
        self.joint_group_application_velocity = numpy.array([joint.application_velocity for joint in self.joints])
        self.joint_group_application_effort = numpy.array([joint.application_effort for joint in self.joints])

        self.joint_group_measured_position = numpy.array([joint.measured_position for joint in self.joints])
        self.joint_group_measured_velocity = numpy.array([joint.measured_velocity for joint in self.joints])
        self.joint_group_measured_effort = numpy.array([joint.measured_effort for joint in self.joints])
        self.joint_group_measured_current = numpy.array([joint.measured_current for joint in self.joints])

        # joint -> joint urdf
        self.joint_urdf_group_measured_position = (self.joint_group_measured_position.copy())
        self.joint_urdf_group_measured_velocity = (self.joint_group_measured_velocity.copy())
        self.joint_urdf_group_measured_effort = (self.joint_group_measured_effort.copy())

        # --------------------------------------------------
        # end effector
        if self.end_effector_group is not None:
            self.end_effector_group.update()
        else:
            for end_effector in self.end_effectors:
                end_effector.update()

        self.end_effector_group_measured_position = numpy.array([end_effector.measured_position for end_effector in self.end_effectors])
        self.end_effector_group_measured_velocity = numpy.array([end_effector.measured_velocity for end_effector in self.end_effectors])
        self.end_effector_group_measured_effort = numpy.array([end_effector.measured_effort for end_effector in self.end_effectors])

        # --------------------------------------------------
        # check data validity
        # if all data in sensor_usb_imu_group_measured_quat is 0,
        # then the data is invalid, log error and return function result fail
        if numpy.all(self.sensor_usb_imu_group_measured_quat == 0):
            if len(self.sensor_usb_imus) > 0:
                if self.sensor_usb_imus[0].comm_enable:
                    Logger().print_error(
                        f"All data in sensor_usb_imu_group_measured_quat is 0. \n"
                        f"IMU may not work properly. Please check IMU connection, power supply, and software version."
                    )
                else:
                    pass

                # Jason 2025-6-27:
                # Only return FAIL when sensor_usb_imus is not empty,
                return FunctionResult.FAIL
            else:
                pass

        return FunctionResult.SUCCESS

    def control_loop_print_state(self) -> FunctionResult:

        # debug print
        if gl_config.parameters.get("debug", {}).get("print_imu_state", False):
            Logger().print_debug(f"sensor_imu_group_measured_quat: "
                                 f"{numpy.round(self.sensor_imu_group_measured_quat, 2)}")
            Logger().print_debug(f"sensor_imu_group_measured_angle: "
                                 f"{numpy.round(self.sensor_imu_group_measured_euler_angle, 2)}")
            Logger().print_debug(f"sensor_imu_group_measured_angular_velocity: "
                                 f"{numpy.round(self.sensor_imu_group_measured_angular_velocity, 2)}")
            Logger().print_debug(f"sensor_imu_group_measured_linear_acceleration: "
                                 f"{numpy.round(self.sensor_imu_group_measured_linear_acceleration, 2)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_application_position_state", False):
            Logger().print_debug(f"joint_group_application_position: "
                                 f"{numpy.round(self.joint_group_application_position, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_application_velocity_state", False):
            Logger().print_debug(f"joint_group_application_velocity: "
                                 f"{numpy.round(self.joint_group_application_velocity, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_application_effort_state", False):
            Logger().print_debug(f"joint_group_application_effort: "
                                 f"{numpy.round(self.joint_group_application_effort, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_position_state", False):
            Logger().print_debug(f"joint_group_measured_position: "
                                 f"{numpy.round(self.joint_group_measured_position, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_velocity_state", False):
            Logger().print_debug(f"joint_group_measured_velocity: "
                                 f"{numpy.round(self.joint_group_measured_velocity, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_effort_state", False):
            Logger().print_debug(f"joint_group_measured_effort: "
                                 f"{numpy.round(self.joint_group_measured_effort, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_current_state", False):
            Logger().print_debug(f"joint_group_measured_current: "
                                 f"{numpy.round(self.joint_group_measured_current, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_urdf_position_state", False):
            Logger().print_debug(f"joint_urdf_group_measured_position: "
                                 f"{numpy.round(self.joint_urdf_group_measured_position, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_urdf_velocity_state", False):
            Logger().print_debug(f"joint_urdf_group_measured_velocity: "
                                 f"{numpy.round(self.joint_urdf_group_measured_velocity, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_joint_urdf_effort_state", False):
            Logger().print_debug(f"joint_urdf_group_measured_effort: "
                                 f"{numpy.round(self.joint_urdf_group_measured_effort, 3)}")

        if gl_config.parameters.get("debug", {}).get("print_ioboard_state", False):
            for i in range(self.number_of_ioboard):
                if self.ioboards[i] is None:
                    continue
                ioboard = self.ioboards[i]
                Logger().print_debug(
                    f"[ioboard {i}] ip={ioboard.ip} "
                    f"system_state={ioboard.system_state} "
                    f"emergency_state={ioboard.emergency_state} "
                    f"battery_voltage={ioboard.battery_voltage:.3f}V "
                    f"battery_voltage_percent={ioboard.battery_voltage_percent} "
                    f"robot_charging_level={ioboard.robot_charging_level} "
                    f"robot_charging_state={ioboard.robot_charging_state} "
                    f"timeout={ioboard.flag_timeout}"
                )

        return FunctionResult.SUCCESS

    def control_loop_print_command(self) -> FunctionResult:

        if gl_config.parameters.get("debug", {}).get("print_peripheral_virtual_joystick", False):
            Logger().print_debug(peripheral_virtual_joystick)

        if gl_config.parameters.get("debug", {}).get("print_peripheral_virtual_keyboard", False):
            Logger().print_debug(peripheral_virtual_keyboard)

        if gl_config.parameters.get("debug", {}).get("print_peripheral_virtual_mouse", False):
            Logger().print_debug(peripheral_virtual_mouse)

        if gl_config.parameters.get("debug", {}).get("print_peripheral_virtual_teleoperation", False):
            Logger().print_debug(peripheral_virtual_teleoperation)

        if gl_config.parameters.get("debug", {}).get("print_peripheral_virtual_panel", False):
            Logger().print_debug(peripheral_virtual_panel)

        return FunctionResult.SUCCESS

    def _control_loop_output(self) -> FunctionResult:

        # copy value from actuator to actuator group ... (auto done)
        # copy value from joints to joint group ... (auto done)
        # copy value from end effectors to end effector group ... (auto done)

        # actuator
        self.actuator_group_target_position = numpy.array([actuator.target_position for actuator in self.actuators])
        self.actuator_group_target_velocity = numpy.array([actuator.target_velocity for actuator in self.actuators])
        self.actuator_group_target_effort = numpy.array([actuator.target_effort for actuator in self.actuators])
        self.actuator_group_target_current = numpy.array([actuator.target_current for actuator in self.actuators])

        # joint
        self.joint_group_target_position = numpy.array([joint.target_position for joint in self.joints])
        self.joint_group_target_velocity = numpy.array([joint.target_velocity for joint in self.joints])
        self.joint_group_target_effort = numpy.array([joint.target_effort for joint in self.joints])
        self.joint_group_target_current = numpy.array([joint.target_current for joint in self.joints])

        # end effector
        self.end_effector_group_target_position = numpy.array([end_effector.target_position for end_effector in self.end_effectors])
        self.end_effector_group_target_velocity = numpy.array([end_effector.target_velocity for end_effector in self.end_effectors])
        self.end_effector_group_target_effort = numpy.array([end_effector.target_effort for end_effector in self.end_effectors])

        # output to real robot
        if self.work_space in [RobotWorkSpace.ACTUATOR_SPACE]:
            if self.actuator_group is not None:
                self.actuator_group.download()
            else:
                for actuator in self.actuators:
                    actuator.download()
        elif self.work_space in [RobotWorkSpace.JOINT_SPACE,
                                 RobotWorkSpace.URDF_SPACE,
                                 RobotWorkSpace.TASK_SPACE]:
            if self.joint_group is not None:
                self.joint_group.download()
            else:
                for joint in self.joints:
                    joint.download()
        else:
            pass

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 接口层函数 (Python 开发)

    def _control_loop_update_share_buffer(self) -> FunctionResult.SUCCESS:
        """
        Update the shared data for developer use,
        such as joint states, actuator states, etc.
        """
        # sensor
        numpy.copyto(self.share_sensor_imu_group_measured_quat, self.sensor_imu_group_measured_quat)
        numpy.copyto(self.share_sensor_imu_group_measured_angle, self.sensor_imu_group_measured_euler_angle)
        numpy.copyto(self.share_sensor_imu_group_measured_angular_velocity, self.sensor_imu_group_measured_angular_velocity)
        numpy.copyto(self.share_sensor_imu_group_measured_linear_acceleration, self.sensor_imu_group_measured_linear_acceleration)

        # joint (using joint_urdf, better to fit urdf model)
        numpy.copyto(self.share_joint_urdf_group_measured_position, self.joint_urdf_group_measured_position)
        numpy.copyto(self.share_joint_urdf_group_measured_velocity, self.joint_urdf_group_measured_velocity)
        numpy.copyto(self.share_joint_urdf_group_measured_effort, self.joint_urdf_group_measured_effort)

        # joint
        numpy.copyto(self.share_joint_group_measured_current, self.joint_group_measured_current)

        return FunctionResult.SUCCESS

    def _control_loop_get_state(self) -> dict:
        """
        Get the state of the robot

        Returns:
            dict: the state of the robot
        """

        self.state_dict.update(
            {
                # imu
                "imu_quat": self.share_sensor_imu_group_measured_quat,
                "imu_euler_angle": self.share_sensor_imu_group_measured_angle,
                "imu_angular_velocity": self.share_sensor_imu_group_measured_angular_velocity,
                "imu_acceleration": self.share_sensor_imu_group_measured_linear_acceleration,
                # joint (replace by joint_urdf)
                "joint_position": self.share_joint_urdf_group_measured_position,
                "joint_velocity": self.share_joint_urdf_group_measured_velocity,
                "joint_effort": self.share_joint_urdf_group_measured_effort,
                # joint
                "joint_current": self.share_joint_group_measured_current,
            }
        )

        return self.state_dict

    def _control_loop_set_control(self, control_dict=None) -> FunctionResult:
        if control_dict is None:
            return FunctionResult.SUCCESS

        target_control_mode = control_dict.get("control_mode", None)
        target_position = control_dict.get("position", None)
        target_velocity = control_dict.get("velocity", None)
        target_effort = control_dict.get("effort", None)
        target_current = control_dict.get("current", None)
        target_position_control_kp = control_dict.get("position_control_kp", None)
        target_velocity_control_kp = control_dict.get("velocity_control_kp", None)
        target_velocity_control_ki = control_dict.get("velocity_control_ki", None)
        target_pd_control_kp = control_dict.get("pd_control_kp", None)
        target_pd_control_kd = control_dict.get("pd_control_kd", None)

        # control_dict
        self.work_space = RobotWorkSpace.JOINT_SPACE

        for i, joint in enumerate(self.joints):
            target_control_mode_i = target_control_mode[i] if target_control_mode is not None else None
            target_position_i = target_position[i] if target_position is not None else None
            target_velocity_i = target_velocity[i] if target_velocity is not None else None
            target_effort_i = target_effort[i] if target_effort is not None else None
            target_current_i = target_current[i] if target_current is not None else None
            target_position_control_kp_i = target_position_control_kp[i] if target_position_control_kp is not None else None
            target_velocity_control_kp_i = target_velocity_control_kp[i] if target_velocity_control_kp is not None else None
            target_velocity_control_ki_i = target_velocity_control_ki[i] if target_velocity_control_ki is not None else None
            target_pd_control_kp_i = target_pd_control_kp[i] if target_pd_control_kp is not None else None
            target_pd_control_kd_i = target_pd_control_kd[i] if target_pd_control_kd is not None else None

            if target_control_mode_i == JointControlMode.POSITION:
                joint.set_target_position_control(position=target_position_i)
                joint.set_target_position_control_kp(target_position_control_kp_i)
                joint.set_target_velocity_control_kp(target_velocity_control_kp_i)
                joint.set_target_velocity_control_ki(target_velocity_control_ki_i)

            elif target_control_mode_i == JointControlMode.VELOCITY:
                joint.set_target_velocity_control(velocity=target_velocity_i)
                joint.set_target_velocity_control_kp(target_velocity_control_kp_i)
                joint.set_target_velocity_control_ki(target_velocity_control_ki_i)

            elif target_control_mode_i == JointControlMode.EFFORT:
                joint.set_target_effort_control(effort=target_effort_i)

            elif target_control_mode_i == JointControlMode.CURRENT:
                joint.set_target_current_control(current=target_current_i)

            elif target_control_mode_i == JointControlMode.PD:
                joint.set_target_pd_control(position=target_position_i,
                                            velocity=target_velocity_i,
                                            effort=target_effort_i, )
                joint.set_target_pd_control_kp(target_pd_control_kp_i)
                joint.set_target_pd_control_kd(target_pd_control_kd_i)

            elif target_control_mode_i == JointControlMode.POSITION_PSEUDO_PD:
                target_position_control_kp_i, target_velocity_control_kp_i = \
                    joint.calculate_position_pseudo_pd_kp_kd(
                        target_pd_control_kp_i, target_pd_control_kd_i
                    )
                joint.set_target_position_control_kp(target_position_control_kp_i)
                joint.set_target_velocity_control_kp(target_velocity_control_kp_i)
                joint.set_target_velocity_control_ki(0.0)
                joint.set_target_position_control(position=target_position_i)

            else:
                pass

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 接口层函数 (Zenoh 开发)

    def _control_loop_publish_state(self) -> FunctionResult:
        """
        发布机器人状态到 Zenoh 网络，主要用于数据的共享和发布。
        """

        # 取三位小数
        imu_measured_quat_to_world = numpy.round(self.share_sensor_imu_group_measured_quat, 3)
        imu_measured_angle_to_world = numpy.round(self.share_sensor_imu_group_measured_angle, 3)
        imu_measured_angular_velocity_to_self = numpy.round(self.share_sensor_imu_group_measured_angular_velocity, 3)
        imu_measured_linear_acceleration_to_self = numpy.round(self.share_sensor_imu_group_measured_linear_acceleration, 3)
        joint_measured_position_value = numpy.round(self.share_joint_urdf_group_measured_position, 3)
        joint_measured_velocity_value = numpy.round(self.share_joint_urdf_group_measured_velocity, 3)
        joint_measured_effort_value = numpy.round(self.share_joint_urdf_group_measured_effort, 3)

        # publish state data
        robot_data_dict = {
            "imu_quat": imu_measured_quat_to_world.tolist(),
            "imu_euler_angle": imu_measured_angle_to_world.tolist(),
            "imu_angular_velocity": imu_measured_angular_velocity_to_self.tolist(),
            "imu_linear_acceleration": imu_measured_linear_acceleration_to_self.tolist(),
            "joint_position": joint_measured_position_value.tolist(),
            "joint_velocity": joint_measured_velocity_value.tolist(),
            "joint_effort": joint_measured_effort_value.tolist(),
        }

        task_data_dict = {
            "task_execute": self.task_execute,
            "component_execute": self.component_execute,
        }

        # send zenoh publish message
        self._zenoh_publish_handler(topic="robot", data_dict=robot_data_dict)
        self._zenoh_publish_handler(topic="task", data_dict=task_data_dict)

        return FunctionResult.SUCCESS

    def _zenoh_publish_handler(self, topic: str, data_dict: dict):
        """
        Zenoh 发布数据 (Server -> Client)
        """

        # Convert data_dict to a format suitable for Zenoh publishing
        for key, value in data_dict.items():
            if isinstance(value, (list, tuple)):
                # Convert lists and tuples to lists, handling numpy elements
                data_dict[key] = [float(x) if hasattr(x, 'item') else x for x in value]
            elif hasattr(value, 'item'):  # Handles numpy numeric types (int64, float64, etc.)
                # Convert numpy types to native Python types
                data_dict[key] = float(value.item())
            elif isinstance(value, (int, float)):
                # Convert single values to float for consistency
                data_dict[key] = float(value)
            elif isinstance(value, str):
                # Ensure strings are properly encoded
                data_dict[key] = value.encode('utf-8')  # 默认用 utf-8 解码
            else:
                pass

        data_packed = msgpack.packb(data_dict)

        self._zenoh_publishers[topic].put(data_packed)

    def _zenoh_subscribe_handler(self, sample: zenoh.Sample):
        """
        Zenoh 订阅数据 (Client -> Server)
        """

        key_expr = sample.key_expr
        key_expr_str = str(key_expr)

        # change from builtins.ZBytes to bytes-like object
        sample_value = sample.payload.to_bytes()

        # get the data_dict from the sample_value
        data_dict = msgpack.unpackb(sample_value)

        # Convert data_dict to a format suitable for Python processing
        for key, value in data_dict.items():
            if isinstance(value, bytes):
                data_dict[key] = value.decode('utf-8')  # 默认用 utf-8 解码

        # check if the key_expr_str is in the zenoh_key_exprs for robot subscribers
        if data_dict:
            if key_expr_str in self.zenoh_key_exprs["subscribers"]["robot"]:
                # update joint control mode
                if "group_name" in data_dict:
                    group_name = data_dict["group_name"]

                if "control_mode" in data_dict:
                    self.joint_control_mode = numpy.array(data_dict["control_mode"])

                # update joint PD control parameters
                if "kp" in data_dict:
                    self.joint_pd_control_kp = numpy.array(data_dict["kp"])

                if "kd" in data_dict:
                    self.joint_pd_control_kd = numpy.array(data_dict["kd"])

                # update joint control target
                if "position" in data_dict:
                    self.joint_control_target = numpy.array(data_dict["position"])

                if "command_id" in data_dict:
                    command_id = data_dict["command_id"]

                # 更新 joint control 相关变量
                for i, joint in enumerate(self.joints):
                    target_control_mode_i = self.joint_control_mode[i] if self.joint_control_mode is not None else None

                    if target_control_mode_i == JointControlMode.PD:
                        joint.set_target_pd_control(
                            position=self.joint_control_target[i],
                            velocity=0.0,  # 这里假设没有速度控制
                            effort=0.0,  # 这里假设没有动能控制
                        )
                        joint.set_target_pd_control_kp(self.joint_pd_control_kp[i])
                        joint.set_target_pd_control_kd(self.joint_pd_control_kd[i])
                    else:
                        pass

            if key_expr_str in self.zenoh_key_exprs["subscribers"]["task"]:
                # update task command
                if "task_command" in data_dict:
                    task_command = data_dict["task_command"]
                    self.set_task_command(task_command=task_command, value_type="value")

                if "component_command" in data_dict:
                    component_command = data_dict["component_command"]
                    self.set_component_command(component_command=component_command, value_type="value")

                if "command_id" in data_dict:
                    command_id = data_dict["command_id"]

    # =====================================================================================================
