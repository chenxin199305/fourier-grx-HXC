import time
import numpy

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.sensor import SensorUSBIMUForsense
from fourier_core.actuator import ActuatorFIACE
from fourier_core.joint import JointRotary

from fourier_grx.predefine import *
from fourier_grx.task import *
from fourier_grx.task.hxc import *  # import all tasks, for registration
from fourier_grx.task.fi_task_registry import TaskRegistry

from fourier_grx.robot.robot_real import RobotReal
from fourier_grx.robot.hxc.fi_robot_hxc_param import *


class RobotHXC(RobotReal):
    def __init__(self):
        super().__init__()

        self._load_param()

        # sensor
        self._init_sensor()

        # actuator
        self._init_actuator()

        # joint
        self._init_joint()

        # link
        self._init_link()

        # end effector
        self._init_end_effector()

        # robot
        self._init_robot()

        # task
        RobotHXC._init_task(self)

    def _create_component(self) -> FunctionResult:
        super()._create_component()

        # sensor
        self._create_component_sensor()

        # actuator
        self._create_component_actuator()

        # joint
        self._create_component_joint()

        # link
        self._create_component_link()

        # end effector
        self._create_component_end_effector()

        # robot
        self._create_component_robot()

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _load_param(self) -> FunctionResult:
        self.robot_param = RobotHXCParam()

        return FunctionResult.SUCCESS

    def _init_sensor(self) -> FunctionResult:
        self.sensor_usb_imus_usb = []

        if gl_config.parameters.get("sensor_usb_imu") is not None:
            self.sensor_usb_imus_usb = \
                gl_config.parameters.get("sensor_usb_imu", {}).get("usb", ["/dev/ttyUSB0"])
        else:
            self.sensor_usb_imus_usb = \
                ["/dev/ttyUSB0"]  # Default : "/dev/ttyUSB0"

        self.number_of_sensor_usb_imu = len(self.sensor_usb_imus_usb)

        return FunctionResult.SUCCESS

    def _init_actuator(self) -> FunctionResult:
        """ Initialize actuator for the robot. """

        """
        Jason 2025-06-29:
        Only classes from RobotReal need to implement the actuator initialization.
        """
        self.number_of_actuator = 3 + 3 + 3 + 3 + 1 + 1 + 1 + 1
        self.actuators_ip = [
            # front left leg (positon control)
            "10",
            "11",
            "12",
            # front right leg (position control)
            "30",
            "31",
            "32",
            # rear left leg (position control)
            "70",
            "71",
            "72",
            # rear right leg (position control)
            "50",
            "51",
            "52",
            # front left leg (velocity control)
            "13",
            # front right leg (velocity control)
            "33",
            # rear left leg (velocity control)
            "73",
            # rear right leg (velocity control)
            "53",
        ]
        self.actuators_type = [
            # front left leg (positon control)
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            # front right leg (position control)
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            # rear left leg (position control)
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            # rear right leg (position control)
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            ActuatorFIACEType.ACE_TYPE_X6_60,
            # front left leg (velocity control)
            ActuatorFIACEType.ACE_TYPE_X10_40,
            # front right leg (velocity control)
            ActuatorFIACEType.ACE_TYPE_X10_40,
            # rear left leg (velocity control)
            ActuatorFIACEType.ACE_TYPE_X10_40,
            # rear right leg (velocity control)
            ActuatorFIACEType.ACE_TYPE_X10_40,
        ]

        return FunctionResult.SUCCESS

    def _init_joint(self) -> FunctionResult:
        self.number_of_joint = self.robot_param.number_of_joint
        self.joints_direction = self.robot_param.joints_direction
        self.joint_home_position = self.robot_param.joint_home_position
        self.joint_max_position = self.robot_param.joint_max_position
        self.joint_min_position = self.robot_param.joint_min_position
        self.joint_kinematic_reduction_ratio = self.robot_param.joint_kinematic_reduction_ratio
        self.joint_kinetic_reduction_ratio = self.robot_param.joint_kinetic_reduction_ratio

        # default PD
        self.joint_pd_control_kp = self.robot_param.joint_pd_control_kp
        self.joint_pd_control_kd = self.robot_param.joint_pd_control_kd

        # --------------------------------------------------

        # body region separation
        self.number_of_leg_body_joints = self.robot_param.number_of_leg_body_joints
        self.number_of_wheel_body_joints = self.robot_param.number_of_wheel_body_joints
        self.number_of_whole_body_joints = self.robot_param.number_of_whole_body_joints

        self.indexes_of_leg_body_joints = self.robot_param.indexes_of_leg_body_joints
        self.indexes_of_wheel_body_joints = self.robot_param.indexes_of_wheel_body_joints
        self.indexes_of_whole_body_joints = self.robot_param.indexes_of_whole_body_joints

        # --------------------------------------------------

        return FunctionResult.SUCCESS

    def _init_link(self) -> FunctionResult:
        self.number_of_link = 0

        return FunctionResult.SUCCESS

    def _init_end_effector(self) -> FunctionResult:
        self.number_of_end_effector = 0

        return FunctionResult.SUCCESS

    def _init_robot(self) -> FunctionResult:
        self.robot_name = gl_config.parameters.get("robot", {}).get("name", RobotName.HXCT1)

        return FunctionResult.SUCCESS

    def _init_task(self) -> FunctionResult:
        for task_cls in TaskRegistry.get_tasks(self.robot_name):
            self._register_task(task_cls)

        self.task_shortcuts.update({
            "esc": TaskMenuRobotReal.TASK_SERVO_OFF,
            # 任务功能快捷键（准备）
            "square": None,
            # 任务功能快捷键（站、走 + 操作）
            "triangle": None,
            # 任务功能快捷键（站、走、跑 + 操作）
            "circle": None,
            # 任务功能快捷键（测试）
            "cross": None,
        })

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _create_component_sensor(self) -> FunctionResult:
        self.sensor_usb_imus = []
        for i in range(self.number_of_sensor_usb_imu):
            self.sensor_usb_imus.append(
                SensorUSBIMUForsense(
                    usb=self.sensor_usb_imus_usb[i],
                    mode=SensorUSBIMUForsense.MODE.RADIANS,
                )
            )

        return FunctionResult.SUCCESS

    def _create_component_actuator(self) -> FunctionResult:
        self.actuators = []
        for i in range(self.number_of_actuator):
            self.actuators.append(
                ActuatorFIACE(
                    ip=self.actuators_ip[i],
                    type=self.actuators_type[i],
                )
            )

        return FunctionResult.SUCCESS

    def _create_component_joint(self) -> FunctionResult:
        self.joints = []
        for i in range(self.number_of_joint):
            self.joints.append(
                JointRotary(
                    actuator=self.actuators[i],
                    direction=self.joints_direction[i],
                    home_position=self.joint_home_position[i],
                    min_position=self.joint_min_position[i],
                    max_position=self.joint_max_position[i],
                    kinematic_reduction_ratio=self.joint_kinematic_reduction_ratio[i],
                    kinetic_reduction_ratio=self.joint_kinetic_reduction_ratio[i],
                )
            )

        # download PD to actuator
        for i in range(self.number_of_joint):
            # set pd control as backup plan
            self.joints[i].set_target_pd_control_kp(self.joint_pd_control_kp[i])
            self.joints[i].set_target_pd_control_kd(self.joint_pd_control_kd[i])

        return FunctionResult.SUCCESS

    def _init(self) -> FunctionResult:
        # initialize all joints (downloads PD params for every joint)
        result = super()._init()
        if result != FunctionResult.SUCCESS:
            return result

        Logger().print_info(f"{self.__class__.__name__} _init() download VELOCITY params for wheel joints...")

        # wheel joints use velocity control — override the PD param download done by the base class
        for i in self.indexes_of_wheel_body_joints:
            retry_count = 0
            retry_max = 5
            result = FunctionResult.FAIL

            while result == FunctionResult.FAIL:
                result = self.joints[i].download_control_pid(
                    assign_control_mode=JointControlMode.VELOCITY,
                    pass_repeat=False,
                )

                retry_count += 1
                if retry_count >= retry_max:
                    Logger().print_error(
                        f"{self.__class__.__name__} _init() wheel joint {i} velocity param download failed!"
                    )
                    break

        Logger().print_info("Wheel joint VELOCITY param setup OK!")

        return FunctionResult.SUCCESS

    def _create_component_link(self) -> FunctionResult:
        self.links = []

        return FunctionResult.SUCCESS

    def _create_component_end_effector(self) -> FunctionResult:
        self.end_effectors = []

        return FunctionResult.SUCCESS

    def _create_component_robot(self) -> FunctionResult:
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _prepare(self) -> FunctionResult:
        if (
                self.deploy_mode == DeployMode.DEFAULT
                or self.deploy_mode == DeployMode.DEVELOPER_MODE
                or self.deploy_mode == DeployMode.SDK_MODE
        ):
            # update --------------------------------------------------------------

            # read current joint position
            # Jason 2024-01-26:
            # need to wait and send twice to allow data to upload
            for actuator in self.actuators:
                actuator.upload()

            time.sleep(0.01)

            for joint in self.joints:
                joint.update()

            time.sleep(0.01)

            for actuator in self.actuators:
                actuator.upload()

            time.sleep(0.01)

            for joint in self.joints:
                joint.update()

            for i in range(self.number_of_joint):
                self.joint_group_measured_position[i] = self.joints[i].measured_position
                self.joint_group_measured_velocity[i] = self.joints[i].measured_velocity
                self.joint_group_measured_effort[i] = self.joints[i].measured_effort
                self.joint_group_measured_current[i] = self.joints[i].measured_current

        else:
            Logger().print_warning("Unknown deploy mode: " + str(self.deploy_mode))

        return FunctionResult.SUCCESS

    def _ready_state(self) -> FunctionResult:
        if self.check_task_command(task_command=TaskMenuGRX.TASK_APPLICATION_STAND_MOTION_CONTROL):
            self.set_task_command(task_command=TaskMenuGRX.TASK_APPLICATION_STAND_MOTION_CONTROL)

        return FunctionResult.SUCCESS

    # =====================================================================================================
