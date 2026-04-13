import numpy

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.hxc.fi_algorithm_hxc_base import (
    AlgorithmHXCBaseControlModel,
)
from fourier_grx.algorithm.fi_algorithm_math_base import (
    quat_rotate_inverse,
)


class TaskHXCBase(TaskBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmHXCBaseControlModel()
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _init_buffers(self) -> FunctionResult:
        """
        初始化输入输出缓冲区。
        """

        # FIXME: 部分 Task class 没有 task_model，只是一个组合任务。所以，这里需要针对这种情况，特殊处理。
        if self.task_model is None:
            return FunctionResult.SUCCESS

        # input buffers
        self.robot_imu_quat = None
        self.robot_imu_euler_angle = None
        self.robot_imu_angular_velocity = None
        self.robot_imu_linear_acceleration = None

        self.robot_joint_position = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_velocity = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_effort = numpy.zeros(self.task_model.number_of_joint)

        # output buffers
        self.work_space = RobotWorkSpace.NONE
        self.joint_target_control_mode = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_kp = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_kd = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_position = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_velocity = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_effort = numpy.zeros(self.task_model.number_of_joint)
        self.joint_target_current = numpy.zeros(self.task_model.number_of_joint)

        self.robot_work_space = RobotWorkSpace.NONE
        self.robot_joint_target_control_mode = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_kp = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_kd = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_position = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_velocity = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_effort = numpy.zeros(self.task_model.number_of_joint)
        self.robot_joint_target_current = numpy.zeros(self.task_model.number_of_joint)

        self.robot_joint_default_position_whole_body = numpy.zeros(self.task_model.number_of_joint_whole_body)
        self.robot_joint_default_velocity_whole_body = numpy.zeros(self.task_model.number_of_joint_whole_body)

        return FunctionResult.SUCCESS

    def _input_buffer_normalization(
            self,
            include_imu: bool = True,
            include_joint: bool = True,
            **kwargs,
    ) -> FunctionResult:
        """
        将输入数据进行归一化处理，主要是将传感器数据转换为算法所需的格式和单位。
        """

        # import
        from fourier_grx.robot.robot_real.fi_robot_real import RobotReal

        # model
        robot = self.fsm_manager

        # 是否包含 IMU 的归一化处理
        if include_imu:
            if isinstance(robot, RobotReal):
                self.robot_imu_quat = robot.sensor_imu_group_measured_quat.copy()  # unit: none
                self.robot_imu_euler_angle = robot.sensor_imu_group_measured_euler_angle.copy()  # unit: rad
                self.robot_imu_angular_velocity = robot.sensor_imu_group_measured_angular_velocity.copy()  # unit: rad/s
                self.robot_imu_linear_acceleration = robot.sensor_imu_group_measured_linear_acceleration.copy()  # unit: m/s^2

        # 是否包含关节的归一化处理
        if include_joint:
            if isinstance(robot, RobotReal):
                self.robot_joint_position = robot.joint_group_measured_position.copy()  # unit : rad
                self.robot_joint_velocity = robot.joint_group_measured_velocity.copy()  # unit : rad/s
                self.robot_joint_effort = robot.joint_group_measured_effort.copy()  # unit : N.m or N

        return FunctionResult.SUCCESS

    def _output_buffer_normalization(
            self,
            **kwargs,
    ) -> FunctionResult:
        """
        将输出数据进行归一化处理，主要是将算法输出的数据转换为机器人所需的格式和单位。
        """

        # import
        from fourier_grx.robot.robot_real.fi_robot_real import RobotReal

        # model
        robot = self.fsm_manager

        self.robot_work_space = self.work_space

        if isinstance(robot, RobotReal):
            self.robot_joint_target_control_mode = self.joint_target_control_mode
            self.robot_joint_target_kp = (
                self.joint_target_kp
                if hasattr(self, 'joint_target_kp') and self.joint_target_kp is not None
                else None
            )  # unit: none
            self.robot_joint_target_kd = (
                self.joint_target_kd
                if hasattr(self, 'joint_target_kd') and self.joint_target_kd is not None
                else None
            )  # unit: none
            self.robot_joint_target_position = (
                self.joint_target_position
                if hasattr(self, 'joint_target_position') and self.joint_target_position is not None
                else None
            )  # unit : rad
            self.robot_joint_target_velocity = (
                self.joint_target_velocity
                if hasattr(self, 'joint_target_velocity') and self.joint_target_velocity is not None
                else None
            )  # unit : rad/s
            self.robot_joint_target_effort = (
                self.joint_target_effort
                if hasattr(self, 'joint_target_effort') and self.joint_target_effort is not None
                else None
            )  # unit : N.m or N
            self.robot_joint_target_current = (
                self.joint_target_current
                if hasattr(self, 'joint_target_current') and self.joint_target_current is not None
                else None
            )  # unit : A
        else:
            pass

        if isinstance(robot, RobotReal):
            self.robot_joint_default_position_whole_body = \
                self.task_model.joint_default_position_real_robot_whole_body.copy()  # unit : rad
            self.robot_joint_default_velocity_whole_body = \
                self.task_model.joint_default_velocity_real_robot_whole_body.copy()  # unit : rad/s
        else:
            pass

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def function_on_activate(self, **kwargs) -> FunctionResult:
        """
        在任务开始时调用，主要是初始化任务模型。
        """

        # init buffers
        self._init_buffers()

        # import
        from fourier_grx.robot.robot_real.fi_robot_real import RobotReal

        # model
        robot = self.fsm_manager

        if isinstance(robot, RobotReal):
            # 使能执行器
            robot.work_space = RobotWorkSpace.ACTUATOR_SPACE
            for i in range(robot.number_of_actuator):
                robot.actuators[i].set_target_control_mode(ActuatorControlMode.SERVO_ON)

            Logger().print_info(f"{self.__class__.__name__}.function_on_activate: Enabled actuators in real robot.")

            # 跳过算法执行标志位
            self.bypass_at_first_run = True

        else:
            pass

        return FunctionResult.SUCCESS

    # =====================================================================================================

    @staticmethod
    def _apply_joint_target(robot, index: int, control_mode, kp, kd, position, velocity, effort, current) -> None:
        """Apply control mode, gains, and the appropriate target to one joint.

        Control mode dispatch:
          POSITION / PD / POSITION_PSEUDO_PD  →  set_target_position
          VELOCITY                             →  set_target_velocity
          EFFORT                               →  set_target_effort
          CURRENT                              →  set_target_current
          NONE / OTHER                         →  no target setter called
        """
        robot.joints[index].set_target_control_mode(control_mode)
        robot.joints[index].set_target_pd_control_kp(kp)
        robot.joints[index].set_target_pd_control_kd(kd)

        match control_mode:
            case JointControlMode.POSITION | JointControlMode.PD | JointControlMode.POSITION_PSEUDO_PD:
                robot.joints[index].set_target_position(position)
            case JointControlMode.VELOCITY:
                robot.joints[index].set_target_velocity(velocity)
            case JointControlMode.EFFORT:
                robot.joints[index].set_target_effort(effort)
            case JointControlMode.CURRENT:
                robot.joints[index].set_target_current(current)
            case _:
                pass  # NONE / OTHER: control mode is set above; no target value needed

    # =====================================================================================================

    def _function_component_output(self) -> FunctionResult:
        """
        任务的主要功能函数，负责将算法的输出应用到机器人上。
        """

        # import
        from fourier_grx.robot.robot_base.fi_robot_base import RobotBase

        # model
        robot: RobotBase = self.fsm_manager

        # match to the real robot target part
        robot_work_space = self.robot_work_space
        robot_joint_target_control_mode = self.robot_joint_target_control_mode
        robot_joint_target_kp = self.robot_joint_target_kp
        robot_joint_target_kd = self.robot_joint_target_kd
        robot_joint_target_position = self.robot_joint_target_position
        robot_joint_target_velocity = self.robot_joint_target_velocity
        robot_joint_target_effort = self.robot_joint_target_effort
        robot_joint_target_current = self.robot_joint_target_current

        # --------------------------------------------------

        robot.work_space = robot_work_space
        for i in range(self.task_model.number_of_joint):
            index = self.task_model.index_of_joints_real_robot[i]
            self._apply_joint_target(
                robot, index,
                robot_joint_target_control_mode[i],
                robot_joint_target_kp[i],
                robot_joint_target_kd[i],
                robot_joint_target_position[i],
                robot_joint_target_velocity[i],
                robot_joint_target_effort[i],
                robot_joint_target_current[i],
            )

        # --------------------------------------------------

        return FunctionResult.SUCCESS

    def _function_standalone_output(self) -> FunctionResult:
        """
        任务的主要功能函数，负责将算法的输出应用到机器人上。
        """

        # import
        from fourier_grx.robot.robot_base.fi_robot_base import RobotBase

        # model
        robot: RobotBase = self.fsm_manager

        # match to the real robot whole body
        robot_work_space = self.robot_work_space
        robot_joint_target_control_mode = self.task_model.control_mode_real_robot_whole_body.copy()
        robot_joint_target_kp = self.task_model.pd_control_kp_real_robot_whole_body.copy()
        robot_joint_target_kd = self.task_model.pd_control_kd_real_robot_whole_body.copy()
        robot_joint_target_position = self.robot_joint_default_position_whole_body
        robot_joint_target_velocity = self.robot_joint_default_velocity_whole_body.copy()
        robot_joint_target_effort = numpy.zeros(self.task_model.number_of_joint_whole_body)
        robot_joint_target_current = numpy.zeros(self.task_model.number_of_joint_whole_body)

        for i in range(self.task_model.number_of_joint):
            index = self.task_model.index_of_joints_real_robot[i]

            robot_joint_target_control_mode[index] = self.robot_joint_target_control_mode[i]
            robot_joint_target_kp[index] = self.robot_joint_target_kp[i]
            robot_joint_target_kd[index] = self.robot_joint_target_kd[i]
            robot_joint_target_position[index] = self.robot_joint_target_position[i]
            robot_joint_target_velocity[index] = self.robot_joint_target_velocity[i]
            robot_joint_target_effort[index] = self.robot_joint_target_effort[i]
            robot_joint_target_current[index] = self.robot_joint_target_current[i]

        # --------------------------------------------------

        robot.work_space = robot_work_space
        for i in range(robot.number_of_joint):
            self._apply_joint_target(
                robot, i,
                robot_joint_target_control_mode[i],
                robot_joint_target_kp[i],
                robot_joint_target_kd[i],
                robot_joint_target_position[i],
                robot_joint_target_velocity[i],
                robot_joint_target_effort[i],
                robot_joint_target_current[i],
            )

        # --------------------------------------------------

        return FunctionResult.SUCCESS

    def function_component(self, **kwargs) -> FunctionResult:
        self._input_buffer_normalization()
        self._function_meta(**kwargs)
        self._output_buffer_normalization()
        self._function_component_output()

        return FunctionResult.SUCCESS

    def function_standalone(self, **kwargs) -> FunctionResult:
        self._input_buffer_normalization()
        self._function_meta(**kwargs)
        self._output_buffer_normalization()
        self._function_standalone_output()

        return FunctionResult.SUCCESS

    # =====================================================================================================
