import numpy

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.hxc import (
    AlgorithmHXCLegBodyRLWalkAirtimeControlModel,
)
from fourier_grx.task.hxc.fi_task_hxc_base import (
    TaskHXCBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.HXCT1,
)
class TaskHXCLegBodyRLWalkAirtime(TaskHXCBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        super().register(fsm_manager=fsm_manager)

        self.task_model = AlgorithmHXCLegBodyRLWalkAirtimeControlModel(dt=self.fsm_manager.control_period)
        self.task_key = TaskMenuHXC.TASK_LEG_BODY_RL_WALK_AIRTIME

        self.commands = numpy.array([0.0, 0.0, 0.0])
        self.commands_filter_inited = False

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def init_filter(self) -> FunctionResult:
        # 如果已经初始化过了，就不再初始化
        if self.commands_filter_inited:
            return

        self.commands_filter_inited = True

        """
        Jason 2024-12-25:
        指令信号一阶滤波器，主要过滤掉一些来自于手柄或是其他外设的高频毛刺信号
        """
        self.commands_filter_cutoff_frequency = 50.0  # Hz
        self.commands_filter_tau = 1 / (2 * numpy.pi * self.commands_filter_cutoff_frequency)
        self.commands_filter_alpha = self.commands_filter_tau / (self.commands_filter_tau + self.fsm_manager.control_period)

        return FunctionResult.SUCCESS

    def commands_filter(self, commands):
        self.init_filter()

        """
        Jason 2024-12-25:
        这里加指令滤波器，会带来一个问题，就是在 rlwalk 的 gait generator，它是根据指令的值大小，生成 stand / walk 指令的。
        由于滤波器的加入，当指令出现过零点时，它过零点的时间会比较长，从而导致 gait generator 可能会误判。

        比如，
        - 实际的操作是 -1.0 -> +1.0，瞬间拉杆就切换过去了，中间可能希望机器人一直保持行走状态。
        - 但是，由于 -1.0 -> -0.1 -> +0.1 -> +1.0，中间 -0.1 -> +0.1 时间比较长，
            gait generator 就是生成站立的指令状态曲线，导致机器人先尝试站立，后续又尝试行走起来的问题。
        """
        self.commands = self.commands_filter_alpha * self.commands + (1 - self.commands_filter_alpha) * commands

        return self.commands

    # =====================================================================================================

    def function_on_enter(self, **kwargs) -> FunctionResult:

        # 读取外设指令 (lin_vel_x, lin_vel_y, ang_vel_yaw)
        commands = TaskCommonTool.read_peripheral_to_xyyaw_vel_commands(self.task_model)

        # 指令滤波器
        self.commands = self.commands_filter(commands=commands)

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:

        base_measured_quat_to_world = self.robot_imu_quat
        base_measured_rpy_vel_to_self = self.robot_imu_angular_velocity

        joint_measured_position = self.robot_joint_position
        joint_measured_velocity = self.robot_joint_velocity

        joint_measured_position_leg_body = numpy.zeros(self.task_model.number_of_joint)
        joint_measured_velocity_leg_body = numpy.zeros(self.task_model.number_of_joint)

        for i in range(self.task_model.number_of_joint):
            index = self.task_model.index_of_joints_real_robot[i]
            joint_measured_position_leg_body[i] = joint_measured_position[index]
            joint_measured_velocity_leg_body[i] = joint_measured_velocity[index]

        # TODO 2024-07-09: use default target position -> urdf joint target position
        init_output = self.task_model.joint_default_position

        # --------------------------------------------------

        joint_target_position_leg_body = \
            self.task_model.run(
                init_output=init_output,
                commands=self.commands,
                base_measured_quat_to_world=base_measured_quat_to_world,
                base_measured_rpy_vel_to_self=base_measured_rpy_vel_to_self,
                joint_measured_position=joint_measured_position_leg_body,
                joint_measured_velocity=joint_measured_velocity_leg_body,
            )

        work_space = RobotWorkSpace.URDF_SPACE
        joint_target_kp_leg_body = self.task_model.pd_control_kp_real_robot.copy()  # unit: none
        joint_target_kd_leg_body = self.task_model.pd_control_kd_real_robot.copy()  # unit: none
        joint_target_position_leg_body = joint_target_position_leg_body  # unit : rad

        # --------------------------------------------------

        self.work_space = work_space
        self.joint_target_kp = joint_target_kp_leg_body
        self.joint_target_kd = joint_target_kd_leg_body
        self.joint_target_control_mode = [JointControlMode.PD] * self.task_model.number_of_joint
        self.joint_target_position = joint_target_position_leg_body

        # --------------------------------------------------

        return FunctionResult.SUCCESS

    # =====================================================================================================
