import numpy
from fourier_core.predefine import FunctionResult, JointControlMode

from fourier_grx.algorithm.hxc.fi_algorithm_hxc_whole_body_steer_drive import (
    AlgorithmHXCWholeBodySteerDriveControlModel,
)
from fourier_grx.fsm import FSMManager
from fourier_grx.peripheral import (
    peripheral_joystick,
    peripheral_virtual_joystick,
)
from fourier_grx.predefine import RobotName, RobotWorkSpace
from fourier_grx.robot.hxc.fi_robot_hxc_param import RobotHXCParam
from fourier_grx.task.common.fi_task_common_tool import clip_to_range, scale_norm_to_range
from fourier_grx.task.fi_task_registry import TaskRegistry
from fourier_grx.task.hxc.fi_task_hxc_base import TaskHXCBase
from fourier_grx.task.menu import TaskMenuHXC


@TaskRegistry.register(
    RobotName.HXCT1,
)
class TaskHXCWholeBodySteerDrive(TaskHXCBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Whole-body HXC steering + wheel-drive control.

        Data flow (every 20 ms):
          Sensor (16 joint positions)
            + peripheral commands
            → whole-body steering-drive algorithm
            → PD targets for leg joints
            + VELOCITY targets for wheel joints

        Command mapping:
          - left stick X  -> steering angle (third joint of each leg)
          - right stick Y -> wheel speed
        """
        super().register(fsm_manager=fsm_manager)

        assert self.fsm_manager is not None

        self.task_model = AlgorithmHXCWholeBodySteerDriveControlModel(dt=self.fsm_manager.control_period)
        self.task_key = TaskMenuHXC.TASK_WHOLE_BODY_STEER_DRIVE

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _read_commands(self) -> numpy.ndarray:
        commands = numpy.zeros(2, dtype=float)

        steering_range = self.task_model.command_steering_angle_range[0]
        wheel_range = self.task_model.command_wheel_velocity_range[0]

        if peripheral_joystick is not None:
            axis_left = numpy.asarray(peripheral_joystick.axis_left(), dtype=float)
            axis_right = numpy.asarray(peripheral_joystick.axis_right(), dtype=float)
            commands[0] = scale_norm_to_range(-axis_left[0], steering_range)
            commands[1] = scale_norm_to_range(-axis_right[1], wheel_range)

        if peripheral_virtual_joystick is not None:
            axis_left = numpy.asarray(peripheral_virtual_joystick.axis_left(), dtype=float)
            axis_right = numpy.asarray(peripheral_virtual_joystick.axis_right(), dtype=float)
            commands[0] = scale_norm_to_range(-axis_left[0], steering_range)
            commands[1] = scale_norm_to_range(-axis_right[1], wheel_range)

        commands[0] = clip_to_range(commands[0], steering_range)
        commands[1] = clip_to_range(commands[1], wheel_range)

        return commands

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:
        joint_pos_full = self.robot_joint_position

        commands = self._read_commands()
        steering_angle = commands[0]
        wheel_velocity = commands[1]

        n = self.task_model.number_of_joint
        joint_pos_algo = numpy.zeros(n)
        for i in range(n):
            idx = self.task_model.index_of_joints_real_robot[i]
            joint_pos_algo[i] = joint_pos_full[idx]

        joint_target_position, joint_target_velocity = self.task_model.run(
            joint_measured_position=joint_pos_algo,
            steering_angle=steering_angle,
            wheel_velocity=wheel_velocity,
        )

        wheel_indices = set(RobotHXCParam.indexes_of_wheel_body_joints.tolist())
        joint_target_control_mode = [
            JointControlMode.VELOCITY if i in wheel_indices else JointControlMode.PD
            for i in range(n)
        ]

        self.work_space = RobotWorkSpace.JOINT_SPACE
        self.joint_target_control_mode = joint_target_control_mode
        self.joint_target_kp = self.task_model.pd_control_kp_real_robot.copy()
        self.joint_target_kd = self.task_model.pd_control_kd_real_robot.copy()
        self.joint_target_position = joint_target_position
        self.joint_target_velocity = joint_target_velocity

        return FunctionResult.SUCCESS
