import sys
import time
import numpy
import threading

from fourier_core import __version__ as fourier_core_version
from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.hardware import *
from fourier_core.sensor import SensorManager
from fourier_core.actuator import ActuatorManager

from fourier_grx import __version__ as fourier_grx_version
from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.comm import *
from fourier_grx.peripheral import *

from fourier_grx.task import *
from fourier_grx.task.robot_base import *  # import all tasks, for registration
from fourier_grx.task.fi_task_registry import TaskRegistry


class RobotBase(FSMManager):
    """
    Robot base class, indeed a task manager to run different tasks under different commands
    """

    def __init__(self):
        super().__init__()

        # info
        self.fourier_core_version = fourier_core_version
        self.fourier_grx_version = fourier_grx_version

        # dicts
        self.state_dict = {}
        self.control_dict = {}

        # flags
        self.flag_task_command_update = FlagState.CLEAR

        self.flag_self_check = FlagState.CLEAR
        self.flag_calibration = FlagState.CLEAR
        self.flag_servo_on = FlagState.CLEAR
        self.flag_emergent_stop = FlagState.CLEAR
        self.flag_fault = FlagState.CLEAR
        self.flag_error = FlagState.CLEAR
        self.flag_pinched = FlagState.CLEAR
        self.flag_over_load = FlagState.CLEAR
        self.flag_torque_protection = FlagState.CLEAR

        self.flag_end_effector_position_protection = FlagState.CLEAR
        self.flag_end_effector_velocity_protection = FlagState.CLEAR
        self.flag_end_effector_effort_protection = FlagState.CLEAR

        self.flag_task_running = FlagState.CLEAR

        self.chip_serial_number_1 = 0
        self.chip_serial_number_2 = 0
        self.chip_serial_number_3 = 0

        self.robot_serial_number = 0

        self.robot_command = 0
        self.robot_state = RobotState.NONE

        self.fence_type = 0
        self.work_space = RobotWorkSpace.NONE

        self.control_period = 0  # unit: s

        self.control_check_frequency: bool = False
        if gl_config.parameters.get("robot", {}).get("control_check_frequency", False) is True:
            self.control_check_frequency = True
        self.control_check_time = 0.0
        self.control_loop_count: int = 0

        self.communication_check_frequency: bool = False
        if gl_config.parameters.get("robot", {}).get("communication_check_frequency", False) is True:
            self.communication_check_frequency = True
        self.communication_check_time = 0.0
        self.communication_loop_count: int = 0

        # managers
        self.hardware_manager = HardwareManager()
        self.sensor_manager = SensorManager()
        self.actuator_manager = ActuatorManager()

        # sensor
        self.number_of_sensor_io_iou = 0

        self.sensor_io_ious: list = []

        self.number_of_sensor_usb_asu = 0
        self.number_of_sensor_usb_odu = 0
        self.number_of_sensor_usb_lcu = 0
        self.number_of_sensor_usb_wsu = 0
        self.number_of_sensor_usb_hcu = 0
        self.number_of_sensor_usb_imu = 0
        self.number_of_sensor_usb_sbu = 0

        self.sensor_usb_asus: list = []
        self.sensor_usb_odus: list = []
        self.sensor_usb_lcus: list = []
        self.sensor_usb_wsus: list = []
        self.sensor_usb_hcus: list = []
        self.sensor_usb_imus: list = []
        self.sensor_usb_sbus: list = []

        self.number_of_sensor_can_asu = 0
        self.number_of_sensor_can_odu = 0
        self.number_of_sensor_can_lcu = 0
        self.number_of_sensor_can_wsu = 0
        self.number_of_sensor_can_hcu = 0
        self.number_of_sensor_can_imu = 0
        self.number_of_sensor_can_sbu = 0

        self.sensor_can_asus: list = []
        self.sensor_can_odus: list = []
        self.sensor_can_lcus: list = []
        self.sensor_can_wsus: list = []
        self.sensor_can_hcus: list = []
        self.sensor_can_imus: list = []
        self.sensor_can_sbus: list = []

        self.number_of_sensor_fi_fse = 0

        self.sensor_fi_fse: list = []

        self.number_of_sensor_imu = 0

        self.sensor_imus: list = []

        self.sensor_imu_group_measured_quat: numpy.ndarray = numpy.array([])
        self.sensor_imu_group_measured_euler_angle: numpy.array = numpy.array([])
        self.sensor_imu_group_measured_angular_velocity: numpy.ndarray = numpy.array([])
        self.sensor_imu_group_measured_linear_acceleration: numpy.ndarray = numpy.array([])

        # actuator io
        self.number_of_ioboard = 0

        self.ioboards: list = []

        # actuator motor
        self.number_of_actuator = 0

        self.actuators: list = []

        self.actuator_group = None
        self.actuator_group_measured_position: numpy.ndarray = numpy.array([])
        self.actuator_group_measured_velocity: numpy.ndarray = numpy.array([])
        self.actuator_group_measured_effort: numpy.ndarray = numpy.array([])
        self.actuator_group_measured_current: numpy.ndarray = numpy.array([])
        self.actuator_group_target_position: numpy.ndarray = numpy.array([])
        self.actuator_group_target_velocity: numpy.ndarray = numpy.array([])
        self.actuator_group_target_effort: numpy.ndarray = numpy.array([])
        self.actuator_group_target_current: numpy.ndarray = numpy.array([])

        # robot
        self.number_of_joint = 0
        self.number_of_link = 0
        self.number_of_end_effector = 0

        self.actuator_status: numpy.ndarray = numpy.array([])
        self.actuator_control_word: numpy.ndarray = numpy.array([])

        self.joints: list = []
        self.joint_position_control_kp: numpy.ndarray = numpy.array([])
        self.joint_velocity_control_kp: numpy.ndarray = numpy.array([])
        self.joint_velocity_control_ki: numpy.ndarray = numpy.array([])
        self.joint_pd_control_kp: numpy.ndarray = numpy.array([])
        self.joint_pd_control_kd: numpy.ndarray = numpy.array([])

        self.joint_group = None
        self.joint_group_measured_position: numpy.ndarray = numpy.array([])
        self.joint_group_measured_velocity: numpy.ndarray = numpy.array([])
        self.joint_group_measured_effort: numpy.ndarray = numpy.array([])
        self.joint_group_measured_current: numpy.ndarray = numpy.array([])
        self.joint_group_target_position: numpy.ndarray = numpy.array([])
        self.joint_group_target_velocity: numpy.ndarray = numpy.array([])
        self.joint_group_target_effort: numpy.ndarray = numpy.array([])
        self.joint_group_target_current: numpy.ndarray = numpy.array([])
        self.joint_group_application_position: numpy.ndarray = numpy.array([])
        self.joint_group_application_velocity: numpy.ndarray = numpy.array([])
        self.joint_group_application_effort: numpy.ndarray = numpy.array([])

        self.links: list = []

        self.end_effectors: list = []

        self.robot_name = RobotName.Base

        # task
        self.task_command = TaskMenuRobotBase.TASK_IDLE
        self.task_state = TaskMenuRobotBase.TASK_IDLE
        self.task_select = TaskMenuRobotBase.TASK_IDLE
        self.task_select_index = 0  # 用于任务选择索引
        self.task_select_direction = 1  # 用于任务选择方向

        RobotBase._init_task(self)

        # deploy
        self.deploy_mode = DeployMode.DEFAULT

        # record (for debug)
        if gl_config.parameters.get("record", {}).get("enable", False) is True:
            self.flag_record = FlagState.SET
        else:
            self.flag_record = FlagState.CLEAR

        self.record_max_length = gl_config.parameters.get("record", {}).get("max_length", 1E10)
        self.record_buffer = {}

        # update from gl_config
        self.control_period = \
            gl_config.parameters.get("robot", {}).get("control_period",
                                                      ControlSystemPeriod.DEFAULT_CTRL_PERIOD)

        if gl_config.parameters.get("hardware", {}).get("use_can", False) is True:
            self.flag_use_can_communication = FlagState.SET
        else:
            self.flag_use_can_communication = FlagState.CLEAR

        if gl_config.parameters.get("hardware", {}).get("use_ethernet", False) is True:
            self.flag_use_ethernet_communication = FlagState.SET
        else:
            self.flag_use_ethernet_communication = FlagState.CLEAR

        # developer related
        self._developer_share_lock = threading.Lock()
        self._developer_control_lock = threading.Lock()

        # control loop setup
        self.create_steps: list = []
        self.init_steps: list = []
        self.update_state_steps: list = []
        self.algorithm_steps: list = []
        self.output_control_steps: list = []
        self.developer_related_steps: list = []
        self.communication_steps: list = []

    # =====================================================================================================

    def _register_task(self, task_class) -> FunctionResult:
        """
        注册任务到任务管理器中。

        参数:
            task_class: 任务类，必须是 TaskBase 的子类。

        返回:
            FunctionResult.SUCCESS: 注册成功。
            FunctionResult.FAIL: 注册失败。

        (fourier-grx 内部使用)
        """

        if not issubclass(task_class, TaskBase):
            Logger().print_error(f"Task class {task_class.__name__} is not a subclass of TaskBase. Registration failed.")
            return FunctionResult.FAIL

        task_name = f"task_{task_class.__name__}"
        setattr(self, task_name, task_class(fsm_manager=self))

        return FunctionResult.SUCCESS

    def _init_task(self) -> FunctionResult:
        """
        初始化任务管理器和任务菜单。

        (fourier-grx 内部使用)
        """

        for task_cls in TaskRegistry.get_tasks(RobotName.Base):
            self._register_task(task_cls)

        self.task_shortcuts.update({
            "logo": TaskMenuRobotReal.TASK_SERVO_OFF,
            "triangle": None,
            "circle": None,
            "square": None,
            "cross": TaskMenuRobotReal.TASK_CLEAR_FAULT,
        })

        return FunctionResult.SUCCESS

    def register_task(self, task_class) -> FunctionResult:
        """
        注册任务到任务管理器中。

        参数:
            task_class: 任务类，必须是 TaskBase 的子类。

        返回:
            FunctionResult.SUCCESS: 注册成功。
            FunctionResult.FAIL: 注册失败。

        (fourier-grx 外部使用)
        """

        return self._register_task(task_class)

    # =====================================================================================================
    # 接口层函数 (Control System)

    def control_loop_intf_set_control_period(self, control_period) -> FunctionResult:
        self.control_period = control_period
        return FunctionResult.SUCCESS

    def control_loop_intf_set_steps(self) -> FunctionResult:
        """
        设置控制循环的各个步骤。
        """
        # --------------------------------------------------
        # Control Schedule
        # List of create steps
        self.create_steps = [
            (self.create_component, "create_component"),
            (self.create_buffer, "create_buffer"),
            (self.create_communication_buffer, "create_communication_buffer"),
        ]

        # List of initialization steps
        self.init_steps = [
            (self.hardware_platform_init, "hardware_platform_init"),
            (self.init, "init"),
            (self.check, "check"),
            (self.subscribe, "subscribe"),
            (self.prepare, "prepare"),
            (self.ready_state, "ready_state"),
            (self.prepare_pub_sub_interface, "prepare_pub_sub_interface"),
        ]

        # List of update steps
        self.update_state_steps = [
            (self.control_loop_update_state, "control_loop_update_state"),
            (self.control_loop_update_command, "control_loop_update_command"),
            (self.control_loop_print_state, "control_loop_print_state"),
            (self.control_loop_print_command, "control_loop_print_command"),
            (self.control_loop_print_period, "control_loop_print_period"),
        ]

        # List of algorithm steps
        self.algorithm_steps = [
            (self.control_loop_algorithm, "control_loop_algorithm"),
            (self.control_loop_protection, "control_loop_protection"),
        ]

        # List of output control steps
        self.output_control_steps = [
            (self.control_loop_output, "control_loop_output"),
        ]

        # List of developer related steps
        self.developer_related_steps = [
            (self.control_loop_update_share_buffer, "control_loop_update_share_buffer"),
            (self.control_loop_publish_state, "control_loop_publish_state"),
        ]

        # --------------------------------------------------
        # Communication Schedule
        # List of communication steps
        self.communication_steps = [
            (self.communication_loop_update_buffer, "communication_loop_update_buffer"),
            (self.communication_loop_publish, "communication_loop_publish"),
            (self.communication_loop_print_period, "communication_loop_print_period"),
        ]

        return FunctionResult.SUCCESS

    def control_loop_intf_init(self) -> FunctionResult:
        for step, name in self.create_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        for step, name in self.init_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def control_loop_intf_update_state(self) -> FunctionResult:
        for step, name in self.update_state_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def control_loop_intf_algorithm(self) -> FunctionResult:
        for step, name in self.algorithm_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def control_loop_intf_output_control(self) -> FunctionResult:
        for step, name in self.output_control_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def control_loop_intf_developer_related(self) -> FunctionResult:
        for step, name in self.developer_related_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def communication_loop_intf_run(self) -> FunctionResult:
        for step, name in self.communication_steps:
            if step() != FunctionResult.SUCCESS:
                Logger().print_error(f"{name} return FunctionResult.FAIL")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def control_loop_intf_get_state(self) -> dict:
        """
        Get the state of the robot

        Returns:
            state_dict: the state of the robot
        """
        return self.control_loop_get_state()

    def control_loop_intf_set_control(self, control_dict=None) -> FunctionResult:
        """
        Set the control of the robot

        Parameters:
            control_dict (dict): the control of the robot
        """
        return self.control_loop_set_control(control_dict)

    # =====================================================================================================

    def create_component(self):
        Logger().print_info("#################################")
        Logger().print_info("Create component...")

        result = self._create_component()

        Logger().print_success("Create component Completed!")
        Logger().print_info("#################################")

        return result

    def create_buffer(self):
        Logger().print_info("#################################")
        Logger().print_info("Create buffer...")

        result = self._create_buffer()

        Logger().print_success("Create buffer Completed!")
        Logger().print_info("#################################")

        return result

    def create_communication_buffer(self):
        Logger().print_info("#################################")
        Logger().print_info("Create communication buffer...")

        if gl_config.parameters.get("dynalink", None) is None:
            result = FunctionResult.SUCCESS
        elif gl_config.parameters.get("dynalink", {}).get("enable", False) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._create_communication_buffer()

        Logger().print_success("Create communication buffer Completed!")
        Logger().print_info("#################################")

        return result

    def hardware_platform_init(self) -> FunctionResult:
        Logger().print_info("#################################")
        Logger().print_info("Hardware platform initialize...")

        result = self.hardware_manager.init()

        Logger().print_success("Hardware platform initialize Completed!")
        Logger().print_info("#################################")

        return result

    def init(self) -> FunctionResult:
        Logger().print_info("#################################")
        Logger().print_info("Robot initialize...")

        result = self._init()

        Logger().print_success("Robot initialize Completed!")
        Logger().print_info("#################################")

        return result

    def check(self) -> FunctionResult:

        Logger().print_info("#################################")
        Logger().print_info("Self-check...")

        # if not connect to device, do not run init()
        if gl_config.parameters.get("device_connected", True) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._check()

        Logger().print_success("Self-check Completed!")
        Logger().print_info("#################################")

        return result

    def subscribe(self) -> FunctionResult:

        Logger().print_info("#################################")
        Logger().print_info("Peripheral subscribe...")

        # if not connect to device, do not run init()
        if gl_config.parameters.get("device_connected", True) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._subscribe()

        Logger().print_success("Peripheral subscribe Completed!")
        Logger().print_info("#################################")

        return result

    def prepare(self) -> FunctionResult:

        Logger().print_info("#################################")
        Logger().print_info("Prepare...")

        result = self._prepare()

        Logger().print_success("Prepare Completed!")
        Logger().print_info("#################################")

        return result

    def ready_state(self) -> FunctionResult:

        Logger().print_info("#################################")
        Logger().print_info("Ready state...")

        result = self._ready_state()

        Logger().print_success("Ready state Completed!")
        Logger().print_info("#################################")

        return result

    def prepare_pub_sub_interface(self) -> FunctionResult:
        """
        准备发布订阅接口，主要用于数据的发布和订阅。
        该方法可以在子类中重载，以实现具体的发布订阅逻辑。
        """
        Logger().print_info("#################################")
        Logger().print_info("Prepare pub/sub interface...")

        if gl_config.parameters.get("pubsub", None) is None:
            result = FunctionResult.SUCCESS
        elif gl_config.parameters.get("pubsub", {}).get("enable", False) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._prepare_pub_sub_interface()

        Logger().print_success("Prepare pub/sub interface Completed!")
        Logger().print_info("#################################")

        return result

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
        return FunctionResult.SUCCESS

    def _create_communication_buffer(self) -> FunctionResult:

        # 说明：dynalink 的对应变量必须要 tolist() 变换为 list 类型，否则在通信部分进行数据处理时会出现错误。
        DynalinkManager().dynalink_robot.sensor_imus_quat_value = [0.0] * (self.number_of_sensor_imu * 4)
        DynalinkManager().dynalink_robot.sensor_imus_euler_angle_value = [0.0] * (self.number_of_sensor_imu * 3)
        DynalinkManager().dynalink_robot.sensor_imus_angular_velocity_value = [0.0] * (self.number_of_sensor_imu * 3)
        DynalinkManager().dynalink_robot.sensor_imus_linear_acceleration_value = [0.0] * (self.number_of_sensor_imu * 3)

        DynalinkManager().dynalink_robot.flag_actuator_installed = [FlagState.SET] * self.number_of_actuator
        DynalinkManager().dynalink_robot.flag_actuator_accessible = [FlagState.SET] * self.number_of_actuator
        DynalinkManager().dynalink_robot.flag_actuator_enables = [FlagState.SET] * self.number_of_actuator
        DynalinkManager().dynalink_robot.flag_actuator_error = [FlagState.CLEAR] * self.number_of_actuator

        DynalinkManager().dynalink_robot.actuator_measured_position = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_measured_velocity = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_measured_effort = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_measured_current = [0.0] * self.number_of_actuator

        DynalinkManager().dynalink_robot.actuator_output_position = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_output_velocity = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_output_effort = [0.0] * self.number_of_actuator
        DynalinkManager().dynalink_robot.actuator_output_current = [0.0] * self.number_of_actuator

        DynalinkManager().dynalink_robot.joint_measured_position = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_measured_velocity = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_measured_effort = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_measured_current = [0.0] * self.number_of_joint

        DynalinkManager().dynalink_robot.joint_output_position = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_output_velocity = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_output_effort = [0.0] * self.number_of_joint
        DynalinkManager().dynalink_robot.joint_output_current = [0.0] * self.number_of_joint

        DynalinkManager().dynalink_robot.end_effector_measured_position = [0.0] * (self.number_of_end_effector * 6)
        DynalinkManager().dynalink_robot.end_effector_measured_velocity = [0.0] * (self.number_of_end_effector * 6)
        DynalinkManager().dynalink_robot.end_effector_measured_acceleration = [0.0] * (self.number_of_end_effector * 6)
        DynalinkManager().dynalink_robot.end_effector_measured_effort = [0.0] * (self.number_of_end_effector * 6)

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 具体实现层函数 (初始化)

    def _init(self) -> FunctionResult:
        """
        初始化机器人硬件平台，完成所有传感器和执行器的初始化。
        """

        # hardware

        # sensor
        for i in range(self.number_of_sensor_io_iou):
            if self.sensor_io_ious[i] is not None:
                self.sensor_io_ious[i].init()

        for i in range(self.number_of_sensor_io_iou):
            if self.sensor_io_ious[i] is not None:
                self.sensor_io_ious[i].comm()

        for i in range(self.number_of_sensor_usb_imu):
            if self.sensor_usb_imus[i] is not None:
                self.sensor_usb_imus[i].init()

        for i in range(self.number_of_sensor_usb_imu):
            if self.sensor_usb_imus[i] is not None:
                self.sensor_usb_imus[i].comm()

        # actuator io
        for i in range(self.number_of_ioboard):
            if self.ioboards[i] is not None:
                self.ioboards[i].init()

        for i in range(self.number_of_ioboard):
            if self.ioboards[i] is not None:
                self.ioboards[i].comm()

        # actuator motor
        for i in range(self.number_of_actuator):
            if self.actuators[i] is not None:
                self.actuators[i].init()

        for i in range(self.number_of_actuator):
            if self.actuators[i] is not None:
                self.actuators[i].comm(enable=True)

        return FunctionResult.SUCCESS

    def _check(self) -> FunctionResult:
        """
        检查设备是否正常连接，如果设备未连接，则退出程序。
        """

        retry_max = 5

        # sensor
        for i in range(self.number_of_sensor_io_iou):
            self._check_device(self.sensor_io_ious[i], "sensor_io_iou", i, retry_max)

        for i in range(self.number_of_sensor_usb_imu):
            self._check_device(self.sensor_usb_imus[i], "sensor_usb_imu", i, retry_max)

        for i in range(self.number_of_sensor_fi_fse):
            self._check_device(self.sensor_fi_fse[i], "sensor_fi_fse", i, retry_max)

        # actuator io
        for i in range(self.number_of_ioboard):
            self._check_device(self.ioboards[i], "ioboard", i, retry_max)

        # actuator motor
        for i in range(self.number_of_actuator):
            self._check_device(self.actuators[i], "actuator", i, retry_max)

        return FunctionResult.SUCCESS

    def _check_device(self, device, device_name, index, retry_max):
        """
        检查设备是否正常连接，如果设备未连接，则退出程序。

        Parameters:
            device: 设备对象
            device_name: 设备名称
            index: 设备索引
            retry_max: 最大重试次数
        """

        if device is None:
            Logger().print_warning(f"check {device_name} [{index}] is None. Pass.")
            return FunctionResult.SUCCESS

        Logger().print_debug(f"check {device_name} {device.id}")

        retry_count = 0
        result = FunctionResult.FAIL

        while result == FunctionResult.FAIL:
            if device is not None:
                result = device.check()
            else:
                break

            retry_count += 1

            if retry_count >= retry_max:
                Logger().print_error(
                    "Self-check fail! "
                    "Please check all devices are connected correctly!"
                )
                sys.exit(FunctionResult.FAIL)

        return result

    def _subscribe(self) -> FunctionResult:
        """
        订阅传感器和执行器数据，主要用于数据的实时更新。
        """

        # sensor
        for i in range(self.number_of_sensor_io_iou):
            if self.sensor_io_ious[i] is not None:
                self.sensor_io_ious[i].subscribe(enable=True)

        for i in range(self.number_of_sensor_usb_imu):
            if self.sensor_usb_imus[i] is not None:
                self.sensor_usb_imus[i].subscribe(enable=True)

        for i in range(self.number_of_sensor_fi_fse):
            if self.sensor_fi_fse[i] is not None:
                self.sensor_fi_fse[i].subscribe(enable=True)

        # actuator io
        for i in range(self.number_of_ioboard):
            if self.ioboards[i] is not None:
                self.ioboards[i].subscribe(enable=True)

        # actuator motor
        for i in range(self.number_of_actuator):
            if self.actuators[i] is not None:
                self.actuators[i].subscribe(enable=True)

        return FunctionResult.SUCCESS

    def _prepare(self) -> FunctionResult:
        """
        准备机器人状态，主要用于设置机器人状态和工作空间等。
        """

        # if not connect to device, do not run init()
        if gl_config.parameters.get("device_connected", True) is False:
            return FunctionResult.SUCCESS

        return FunctionResult.SUCCESS

    def _ready_state(self) -> FunctionResult:
        """
        准备机器人进入空闲状态，主要用于设置机器人任务命令为 TASK_IDLE。
        """

        self.set_task_command(task_command=TaskMenuRobotBase.TASK_IDLE)

        return FunctionResult.SUCCESS

    def _prepare_pub_sub_interface(self) -> FunctionResult:
        """
        准备发布订阅接口，主要用于数据的发布和订阅。
        """

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 具体实现层函数 (控制循环)

    def control_loop_update_state(self) -> FunctionResult:
        """
        更新机器人状态，包括传感器数据、执行器状态、关节状态和末端执行器状态等。
        """

        self.control_loop_update_state_sensor()
        self.control_loop_update_state_actuator()
        self.control_loop_update_state_robot()

        return FunctionResult.SUCCESS

    def control_loop_update_state_sensor(self) -> FunctionResult:
        """
        更新传感器状态，包括 USB 和 CAN 传感器数据的上传。
        """

        # Upload sensor data
        for sensor_list in [self.sensor_can_asus,
                            self.sensor_usb_imus,
                            self.sensor_usb_asus]:
            [sensor.upload() for sensor in sensor_list if sensor is not None]

        return FunctionResult.SUCCESS

    def control_loop_update_state_actuator(self) -> FunctionResult:
        """
        更新执行器状态，包括执行器 IO 和执行器电机的上传。
        """

        # actuator io
        [ioboard.upload() for ioboard in self.ioboards if ioboard is not None]

        # actuator motor
        [actuator.upload() for actuator in self.actuators if actuator is not None]

        return FunctionResult.SUCCESS

    def control_loop_update_state_robot(self) -> FunctionResult:
        """
        更新机器人状态，包括关节和末端执行器的上传和更新。
        """

        # Use list comprehensions for faster execution
        [joint.upload() for joint in self.joints if joint is not None]
        [end_effector.update() for end_effector in self.end_effectors if end_effector is not None]

        return FunctionResult.SUCCESS

    def control_loop_update_command(self) -> FunctionResult:
        """
        更新机器人任务命令，主要用于处理紧急停止状态和其他任务命令。
        """

        task_command = None

        # check emergent stop state...
        if self.flag_emergent_stop == FlagState.SET:
            # 判断当前任务命令是否为 TASK_SERVO_OFF，如果不是，则将任务命令设置为 TASK_SERVO_OFF
            # (确保只执行一次)
            if self.task_execute != TaskMenuRobotReal.TASK_SERVO_OFF:
                task_command = TaskMenuRobotReal.TASK_SERVO_OFF

        self.update(task_command=task_command)

        return FunctionResult.SUCCESS

    def control_loop_print_state(self) -> FunctionResult:
        """
        打印机器人状态信息，包括传感器数据、执行器状态、关节状态和末端执行器状态等。
        """

        return FunctionResult.SUCCESS

    def control_loop_print_command(self) -> FunctionResult:
        """
        打印机器人任务命令信息，包括当前任务命令、状态和选择等。
        """

        return FunctionResult.SUCCESS

    def control_loop_print_period(self) -> FunctionResult:
        """
        打印机器人控制周期信息。
        """
        if self.control_check_frequency is True:
            self.control_loop_count += 1

            # 每秒打印一次控制频率
            if time.time() - self.control_check_time >= 1:
                Logger().print_info(f"control_loop_count = {self.control_loop_count}")
                self.control_loop_count = 0
                self.control_check_time = time.time()

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def control_loop_algorithm(self) -> FunctionResult:
        """
        本方法完成 RobotBase 中属性变量的算法计算过程。
        """

        self.execute()

        return FunctionResult.SUCCESS

    def control_loop_protection(self) -> FunctionResult:
        """
        本方法针对一些特殊状态，进行保护措施，以确保机器人的安全运行。
        """
        self._control_loop_protection()

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def control_loop_output(self) -> FunctionResult:
        """
        本方法完成 RobotBase 中属性变量的设备输出过程。
        """

        """
        Jason 2025-05-11:
        由于这部分的输出在二次开发时会涉及到数据共享与读写竞争问题，因此需要加入锁机制来确保数据的安全性。
        """
        with self._developer_control_lock:
            self._control_loop_output()

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def _control_loop_protection(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def _control_loop_output(self) -> FunctionResult:
        # Inverse kinematic and effort calculation...

        # actuator io
        for ioboard in filter(None, self.ioboards):
            ioboard.download()

        # actuator motor
        if self.work_space in {RobotWorkSpace.ACTUATOR_SPACE}:
            for actuator in filter(None, self.actuators):
                actuator.download()
        elif self.work_space in {RobotWorkSpace.JOINT_SPACE,
                                 RobotWorkSpace.URDF_SPACE,
                                 RobotWorkSpace.TASK_SPACE}:
            for joint in filter(None, self.joints):
                joint.download()
        else:
            self.work_space = RobotWorkSpace.NONE

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 接口层函数 (Python 开发)

    def control_loop_update_share_buffer(self) -> FunctionResult:
        """
        本方法完成 RobotBase 中属性变量的共享更新过程。
        共享数据是指在多个线程中共享的数据，这些数据在不同的线程中被读取和写入。
        """
        with self._developer_share_lock:
            result = self._control_loop_update_share_buffer()

        return result

    def control_loop_get_state(self) -> dict:
        """
        Get the state of the robot

        Returns:
            dict: the state of the robot
        """

        with self._developer_share_lock:
            state_dict = self._control_loop_get_state()

            # get copy value, in case the value be changed during the developer usage process.
            for key in state_dict:
                # if the value is numpy.ndarray, then copy it
                if isinstance(state_dict[key], numpy.ndarray):
                    state_dict[key] = state_dict[key].copy()

                # if the value is list, then copy it
                elif isinstance(state_dict[key], list):
                    state_dict[key] = state_dict[key].copy()

                # if the value is dict, then copy it
                elif isinstance(state_dict[key], dict):
                    state_dict[key] = state_dict[key].copy()

                # if the value is object, then copy it
                elif hasattr(state_dict[key], "copy"):
                    state_dict[key] = state_dict[key].copy()

                # if the value is not in the above types, then do nothing
                else:
                    pass

        return state_dict

    def control_loop_set_control(self, control_dict=None) -> FunctionResult:
        """
        Set the control of the robot

        Parameters:
            control_dict (dict): the control of the robot

        Returns:
            FunctionResult: the result of the function
        """

        """
        Jason 2025-05-11:
        由于这部分的输出在二次开发时会涉及到数据共享与读写竞争问题，因此需要加入锁机制来确保数据的安全性。
        """
        with self._developer_control_lock:
            result = self._control_loop_set_control(control_dict=control_dict)

        return result

    # ---------------------------------------------------------------------------

    def _control_loop_update_share_buffer(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    def _control_loop_get_state(self) -> dict:
        return self.state_dict

    def _control_loop_set_control(self, control_dict=None) -> FunctionResult:
        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 接口层函数 (Zenoh 开发)

    def control_loop_publish_state(self) -> FunctionResult:
        """
        发布机器人状态到 Zenoh 网络，主要用于数据的共享和发布。
        """

        if gl_config.parameters.get("pubsub", None) is None:
            result = FunctionResult.SUCCESS
        elif gl_config.parameters.get("pubsub", {}).get("enable", False) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._control_loop_publish_state()

        return result

    # ---------------------------------------------------------------------------

    def _control_loop_publish_state(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 通信层函数 (Dynalink)

    def communication_loop_update_buffer(self) -> FunctionResult:
        """
        更新 Dynalink 缓冲区，主要用于数据的更新和处理。
        """

        if gl_config.parameters.get("dynalink", None) is None:
            result = FunctionResult.SUCCESS
        elif gl_config.parameters.get("dynalink", {}).get("enable", False) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._communication_loop_update_buffer()
            # result = FunctionResult.SUCCESS

        return result

    def communication_loop_publish(self) -> FunctionResult:
        """
        发布 Dynalink 数据到 Zenoh 网络，主要用于数据的共享和发布。
        """

        if gl_config.parameters.get("dynalink", None) is None:
            result = FunctionResult.SUCCESS
        elif gl_config.parameters.get("dynalink", {}).get("enable", False) is False:
            result = FunctionResult.SUCCESS
        else:
            result = self._communication_loop_publish()
            # result = FunctionResult.SUCCESS

        return result

    def communication_loop_print_period(self) -> FunctionResult:
        """
        打印机器人控制周期信息。
        """
        if self.communication_check_frequency is True:
            self.communication_loop_count += 1

            # 每秒打印一次控制频率
            if time.time() - self.communication_check_time >= 1:
                Logger().print_info(f"communication_loop_count = {self.communication_loop_count}")
                self.communication_loop_count = 0
                self.communication_check_time = time.time()

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def _communication_loop_update_buffer(self) -> FunctionResult:

        # --------------------------------------------------
        # DynalinkManager SERVER -> CLIENT
        # sensor
        DynalinkManager().dynalink_robot.sensor_imus_quat_value = self.sensor_imu_group_measured_quat.copy().tolist()
        DynalinkManager().dynalink_robot.sensor_imus_euler_angle_value = self.sensor_imu_group_measured_euler_angle.copy().tolist()
        DynalinkManager().dynalink_robot.sensor_imus_angular_velocity_value = self.sensor_imu_group_measured_angular_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.sensor_imus_linear_acceleration_value = self.sensor_imu_group_measured_linear_acceleration.copy().tolist()

        # robot
        DynalinkManager().dynalink_robot.actuator_measured_position = self.actuator_group_measured_position.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_measured_velocity = self.actuator_group_measured_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_measured_effort = self.actuator_group_measured_effort.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_measured_current = self.actuator_group_measured_current.copy().tolist()

        DynalinkManager().dynalink_robot.actuator_output_position = self.actuator_group_target_position.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_output_velocity = self.actuator_group_target_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_output_effort = self.actuator_group_target_effort.copy().tolist()
        DynalinkManager().dynalink_robot.actuator_output_current = self.actuator_group_target_current.copy().tolist()

        DynalinkManager().dynalink_robot.joint_application_position = self.joint_group_application_position.copy().tolist()
        DynalinkManager().dynalink_robot.joint_application_velocity = self.joint_group_application_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.joint_application_effort = self.joint_group_application_effort.copy().tolist()

        DynalinkManager().dynalink_robot.joint_measured_position = self.joint_group_measured_position.copy().tolist()
        DynalinkManager().dynalink_robot.joint_measured_velocity = self.joint_group_measured_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.joint_measured_effort = self.joint_group_measured_effort.copy().tolist()
        DynalinkManager().dynalink_robot.joint_measured_current = self.joint_group_measured_current.copy().tolist()

        DynalinkManager().dynalink_robot.joint_output_position = self.joint_group_target_position.copy().tolist()
        DynalinkManager().dynalink_robot.joint_output_velocity = self.joint_group_target_velocity.copy().tolist()
        DynalinkManager().dynalink_robot.joint_output_effort = self.joint_group_target_effort.copy().tolist()
        DynalinkManager().dynalink_robot.joint_output_current = self.joint_group_target_effort.copy().tolist()

        DynalinkManager().dynalink_robot.flag_robot_calibration = self.flag_calibration
        DynalinkManager().dynalink_robot.flag_robot_emergent_stop = self.flag_emergent_stop
        DynalinkManager().dynalink_robot.flag_robot_fault = self.flag_fault
        DynalinkManager().dynalink_robot.flag_robot_error = self.flag_error
        DynalinkManager().dynalink_robot.flag_robot_pinched = self.flag_pinched
        DynalinkManager().dynalink_robot.flag_robot_over_load = self.flag_over_load
        DynalinkManager().dynalink_robot.flag_robot_torque_protection = self.flag_torque_protection

        # task
        DynalinkManager().dynalink_task.flag_task_running = self.flag_task_running
        DynalinkManager().dynalink_task.robot_task_state = self.task_state

        # --------------------------------------------------
        # DynalinkManager CLIENT -> SERVER
        # robot
        if DynalinkManager().dynalink_robot.clear_flag_robot_over_load:
            DynalinkManager().dynalink_robot.flag_robot_over_load = FlagState.CLEAR
            DynalinkManager().dynalink_robot.clear_flag_robot_over_load = FlagState.CLEAR

        if DynalinkManager().dynalink_robot.clear_flag_robot_torque_protection:
            DynalinkManager().dynalink_robot.flag_robot_torque_protection = FlagState.CLEAR
            DynalinkManager().dynalink_robot.clear_flag_robot_torque_protection = FlagState.CLEAR

        # task
        if DynalinkManager().dynalink_task.flag_task_command_update:
            task_command_value = DynalinkManager().dynalink_task.robot_task_command
            task_command = None

            for task in self.tasks:
                if task.value == task_command_value:
                    task_command = task
                    break

            if task_command is None:
                Logger().print_error(f"Task command value {task_command_value} is not supported.")
            else:
                self.set_task_command(task_command=task_command)

            DynalinkManager().dynalink_task.flag_task_command_update = FlagState.CLEAR

        # component
        if DynalinkManager().dynalink_task.flag_component_command_update:
            component_command_value = DynalinkManager().dynalink_task.robot_component_command
            component_command = None

            for component in self.components:
                if component.value == component_command_value:
                    component_command = component
                    break

            if component_command is None:
                Logger().print_error(f"Component command value {component_command_value} is not supported.")
            else:
                self.set_component_command(component_command=component_command)

            DynalinkManager().dynalink_task.flag_component_command_update = FlagState.CLEAR

        # Virtual Peripheral
        if peripheral_virtual_joystick is not None:
            peripheral_virtual_joystick.update(
                button_up=DynalinkManager().dynalink_grx.virtual_joystick_button_up,
                button_down=DynalinkManager().dynalink_grx.virtual_joystick_button_down,
                button_left=DynalinkManager().dynalink_grx.virtual_joystick_button_left,
                button_right=DynalinkManager().dynalink_grx.virtual_joystick_button_right,
                button_l1=DynalinkManager().dynalink_grx.virtual_joystick_button_l1,
                button_l2=DynalinkManager().dynalink_grx.virtual_joystick_button_l2,
                button_r1=DynalinkManager().dynalink_grx.virtual_joystick_button_r1,
                button_r2=DynalinkManager().dynalink_grx.virtual_joystick_button_r2,
                axis_left=DynalinkManager().dynalink_grx.virtual_joystick_axis_left,
                axis_right=DynalinkManager().dynalink_grx.virtual_joystick_axis_right,
            )

        if peripheral_virtual_keyboard is not None:
            peripheral_virtual_keyboard.update(
                key_up=DynalinkManager().dynalink_grx.virtual_keyboard_key_up,
                key_down=DynalinkManager().dynalink_grx.virtual_keyboard_key_down,
                key_left=DynalinkManager().dynalink_grx.virtual_keyboard_key_left,
                key_right=DynalinkManager().dynalink_grx.virtual_keyboard_key_right,
                key_esc=DynalinkManager().dynalink_grx.virtual_keyboard_key_esc,
                key_enter=DynalinkManager().dynalink_grx.virtual_keyboard_key_enter,
                key_f1=DynalinkManager().dynalink_grx.virtual_keyboard_key_f1,
                key_f2=DynalinkManager().dynalink_grx.virtual_keyboard_key_f2,
                key_f3=DynalinkManager().dynalink_grx.virtual_keyboard_key_f3,
                key_f4=DynalinkManager().dynalink_grx.virtual_keyboard_key_f4,
                key_w=DynalinkManager().dynalink_grx.virtual_keyboard_key_w,
                key_a=DynalinkManager().dynalink_grx.virtual_keyboard_key_a,
                key_s=DynalinkManager().dynalink_grx.virtual_keyboard_key_s,
                key_d=DynalinkManager().dynalink_grx.virtual_keyboard_key_d,
                key_q=DynalinkManager().dynalink_grx.virtual_keyboard_key_q,
                key_e=DynalinkManager().dynalink_grx.virtual_keyboard_key_e,
            )

        if peripheral_virtual_mouse is not None:
            peripheral_virtual_mouse.update(
                button_left=DynalinkManager().dynalink_grx.virtual_mouse_button_left,
                button_right=DynalinkManager().dynalink_grx.virtual_mouse_button_right,
                button_middle=DynalinkManager().dynalink_grx.virtual_mouse_button_middle,
                axis=DynalinkManager().dynalink_grx.virtual_mouse_axis,
            )

        if peripheral_virtual_teleoperation is not None:
            peripheral_virtual_teleoperation.update(
                left_handle_pose=DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose,
                right_handle_pose=DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose,
                head_pose=DynalinkManager().dynalink_grx.virtual_teleoperation_head_pose,
                button_left=DynalinkManager().dynalink_grx.virtual_teleoperation_button_left,
                button_right=DynalinkManager().dynalink_grx.virtual_teleoperation_button_right,
            )

        if peripheral_virtual_user is not None:
            peripheral_virtual_user.update(
                upper_leg_length_left=DynalinkManager().dynalink_grx.virtual_user_upper_leg_length_left,
                upper_leg_length_right=DynalinkManager().dynalink_grx.virtual_user_upper_leg_length_right,
                lower_leg_length_left=DynalinkManager().dynalink_grx.virtual_user_lower_leg_length_left,
                lower_leg_length_right=DynalinkManager().dynalink_grx.virtual_user_lower_leg_length_right,
                upper_arm_length_left=DynalinkManager().dynalink_grx.virtual_user_upper_arm_length_left,
                upper_arm_length_right=DynalinkManager().dynalink_grx.virtual_user_upper_arm_length_right,
                lower_arm_length_left=DynalinkManager().dynalink_grx.virtual_user_lower_arm_length_left,
                lower_arm_length_right=DynalinkManager().dynalink_grx.virtual_user_lower_arm_length_right,

                # 针对康复患者的关节限制参数
                knee_restriction_left=DynalinkManager().dynalink_grx.virtual_user_knee_restriction_left,
                knee_restriction_right=DynalinkManager().dynalink_grx.virtual_user_knee_restriction_right,
            )

        if peripheral_virtual_panel is not None:
            peripheral_virtual_panel.update(
                command_param_1=DynalinkManager().dynalink_grx.virtual_panel_command_param_1,
                command_param_2=DynalinkManager().dynalink_grx.virtual_panel_command_param_2,
                command_param_3=DynalinkManager().dynalink_grx.virtual_panel_command_param_3,
                command_param_4=DynalinkManager().dynalink_grx.virtual_panel_command_param_4,
                command_param_5=DynalinkManager().dynalink_grx.virtual_panel_command_param_5,
                command_param_6=DynalinkManager().dynalink_grx.virtual_panel_command_param_6,
                command_param_7=DynalinkManager().dynalink_grx.virtual_panel_command_param_7,
                command_param_8=DynalinkManager().dynalink_grx.virtual_panel_command_param_8,
                command_param_9=DynalinkManager().dynalink_grx.virtual_panel_command_param_9,
                command_switch_1=DynalinkManager().dynalink_grx.virtual_panel_command_switch_1,
                command_switch_2=DynalinkManager().dynalink_grx.virtual_panel_command_switch_2,
                command_switch_3=DynalinkManager().dynalink_grx.virtual_panel_command_switch_3,
                command_switch_4=DynalinkManager().dynalink_grx.virtual_panel_command_switch_4,
                command_switch_5=DynalinkManager().dynalink_grx.virtual_panel_command_switch_5,
                command_picker_1=DynalinkManager().dynalink_grx.virtual_panel_command_picker_1,
                command_picker_2=DynalinkManager().dynalink_grx.virtual_panel_command_picker_2,
                command_picker_3=DynalinkManager().dynalink_grx.virtual_panel_command_picker_3,
                command_start=DynalinkManager().dynalink_grx.virtual_panel_command_start,
                command_stop=DynalinkManager().dynalink_grx.virtual_panel_command_stop,
                command_pause=DynalinkManager().dynalink_grx.virtual_panel_command_pause,
            )

        return FunctionResult.SUCCESS

    def _communication_loop_publish(self) -> FunctionResult:
        from fourier_grx.process.sync.fi_sync_server import SyncServer

        SyncServer().publish()

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def log_robot_info(self):
        Logger().print_info("#################################")
        Logger().print_info("Robot info: ")

        device_types = [
            # sensor
            ("sensor_io_iou", self.number_of_sensor_io_iou, self.sensor_io_ious),
            ("sensor_usb_asu", self.number_of_sensor_usb_asu, self.sensor_usb_asus),
            ("sensor_usb_imu", self.number_of_sensor_usb_imu, self.sensor_usb_imus),
            ("sensor_fi_fse", self.number_of_sensor_fi_fse, self.sensor_fi_fse),
            # actuator
            ("ioboard_v1", self.number_of_ioboard, self.ioboards),
            ("actuator", self.number_of_actuator, self.actuators),
            # joint
            ("joint", self.number_of_joint, self.joints),
            # end effectors
            ("end_effector", self.number_of_end_effector, self.end_effectors),
        ]

        for device_name, device_count, device_list in device_types:
            if device_count > 0:
                Logger().print_info(f"{self.__class__.__name__} {device_name} has {device_count} with id: ")
                for device in device_list:
                    if device is not None:
                        Logger().print_info(device.id)

        return FunctionResult.SUCCESS

    # =====================================================================================================
