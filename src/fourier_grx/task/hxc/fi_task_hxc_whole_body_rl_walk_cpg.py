import numpy

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.hxc import (
    AlgorithmHXCLegBodyRLWalkCPGControlModel,
)
from fourier_grx.task.hxc.fi_task_hxc_base import (
    TaskHXCBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.HXCT1,
)
class TaskHXCWholeBodyRLWalkCPG(TaskHXCBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        RL walk with CPG for the full HXC platform.

        Data flow (every 20 ms):
          Sensor (IMU + 16 joints)
            → map to 12 leg joints
            → RL policy  (AlgorithmHXCLegBodyRLWalkCPGControlModel)
            → PD position targets for 12 leg joints
            + VELOCITY = 0 for 4 wheel joints
              (owned by AlgorithmHXCBaseControlModel.joint_default_velocity_real_robot_whole_body;
               applied by TaskHXCBase._function_standalone_output for uncontrolled whole-body joints)
        """
        super().register(fsm_manager=fsm_manager)

        self.task_model = AlgorithmHXCLegBodyRLWalkCPGControlModel(dt=self.fsm_manager.control_period)
        self.task_key   = TaskMenuHXC.TASK_WHOLE_BODY_RL_WALK_CPG

        self.commands               = numpy.array([0.0, 0.0, 0.0])  # (lin_x, lin_y, ang_yaw)
        self.commands_filter_inited = False

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _init_commands_filter(self) -> None:
        """Initialise the first-order low-pass filter for velocity commands (lazy, one-shot).

        Cutoff at 50 Hz removes high-frequency joystick noise.
        Note (Jason 2024-12-25): the slow zero-crossing introduced by the filter can briefly
        confuse the gait generator — a hard -1.0 → +1.0 joystick sweep lingers near zero
        long enough for the gait generator to insert an unintended stand phase mid-stride.
        """
        if self.commands_filter_inited:
            return

        self.commands_filter_inited = True

        tau                          = 1.0 / (2.0 * numpy.pi * 50.0)  # 50 Hz cutoff
        self.commands_filter_alpha   = tau / (tau + self.fsm_manager.control_period)

    def _filter_commands(self, commands: numpy.ndarray) -> numpy.ndarray:
        """Apply first-order low-pass filter; returns smoothed (lin_x, lin_y, ang_yaw)."""
        self._init_commands_filter()
        self.commands = (
            self.commands_filter_alpha * self.commands
            + (1.0 - self.commands_filter_alpha) * commands
        )
        return self.commands

    # =====================================================================================================

    def function_on_enter(self, **kwargs) -> FunctionResult:
        # Seed the filter with the current peripheral command so the robot starts
        # without ramping up from zero on task entry.
        commands      = TaskCommonTool.read_peripheral_to_xyyaw_vel_commands(self.task_model)
        self.commands = self._filter_commands(commands=commands)
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:

        # ---- 1. Read sensor data ------------------------------------------------
        base_quat    = self.robot_imu_quat              # (4,)  quaternion, world frame
        base_ang_vel = self.robot_imu_angular_velocity  # (3,)  rad/s, body frame

        joint_pos_full = self.robot_joint_position      # (16,) rad
        joint_vel_full = self.robot_joint_velocity      # (16,) rad/s

        # ---- 2. Map to the 12 leg-joint algorithm space ------------------------
        n = self.task_model.number_of_joint             # 12

        joint_pos_leg = numpy.zeros(n)
        joint_vel_leg = numpy.zeros(n)
        for i in range(n):
            idx              = self.task_model.index_of_joints_real_robot[i]
            joint_pos_leg[i] = joint_pos_full[idx]
            joint_vel_leg[i] = joint_vel_full[idx]

        # ---- 3. Run RL policy → position targets for the 12 leg joints ---------
        joint_target_position = self.task_model.run(
            init_output                   = self.task_model.joint_default_position,
            commands                      = self.commands,
            base_measured_quat_to_world   = base_quat,
            base_measured_rpy_vel_to_self = base_ang_vel,
            joint_measured_position       = joint_pos_leg,
            joint_measured_velocity       = joint_vel_leg,
        )

        # Wheel joints (12–15) are outside this task's number_of_joint scope.
        # Their VELOCITY mode + zero target are owned by AlgorithmHXCBaseControlModel
        # (joint_default_velocity_real_robot_whole_body) and applied by
        # TaskHXCBase._function_standalone_output for all uncontrolled whole-body joints.
        self.work_space                = RobotWorkSpace.URDF_SPACE
        self.joint_target_control_mode = [JointControlMode.PD] * n
        self.joint_target_kp           = self.task_model.pd_control_kp_real_robot.copy()
        self.joint_target_kd           = self.task_model.pd_control_kd_real_robot.copy()
        self.joint_target_position     = joint_target_position  # unit: rad

        return FunctionResult.SUCCESS

    # =====================================================================================================
