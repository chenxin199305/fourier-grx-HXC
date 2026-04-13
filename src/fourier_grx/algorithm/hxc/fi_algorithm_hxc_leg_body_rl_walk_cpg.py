import os
import time
import math
import numpy
import torch

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_grx.rl.rl_robot_tool import (
    torch_quat_rotate_inverse,
)

from fourier_grx.predefine import *
from fourier_grx.config.resource import (
    gl_resource,
)
from fourier_grx.algorithm.hxc.fi_algorithm_hxc_leg_body import (
    AlgorithmHXCLegBodyControlModel,
)
from fourier_grx.algorithm.tools.gait_generator_neo import (
    FourierGaitGenerator as GaitGenerator,
)


class AlgorithmHXCLegBodyRLWalkCPGControlModel(AlgorithmHXCLegBodyControlModel):
    def __init__(
            self,
            dt: float = 0.01,
            decimation=None,
            warmup_period=0.2,
            actor_model_file_path=None,
    ):
        """
        LegBody HXC robot control model with RL CPG stack algorithm

        Input:
        - dt: time step, s
        - decimation: decimation factor
        - warmup_period: warm up period, s
        - actor_model_file_path: actor model file path
        """
        super().__init__()

        # --------------------------------------------------------------------
        # dt and other parameters
        self.control_frequency: float = 50.0
        self.dt: float = dt

        if decimation:
            self.decimation: int = int(decimation)
        else:
            self.decimation: int = int((1 / self.control_frequency) / self.dt)

        self.decimation_count = 0

        # --------------------------------------------------------------------
        # warm up
        self.warmup_period: float = warmup_period
        self.warmup_start_time: float | None = None

        # --------------------------------------------------------------------
        # model file path
        self.actor_model_file_path: str | None = actor_model_file_path

        # --------------------------------------------------------------------
        # for real robot
        self.joint_default_position_real_robot_whole_body = numpy.array([
            0.0, +0.35, 0.0,  # left rear leg (position control)
            0.0, -0.35, 0.0,  # right rear leg (position control)
            0.0, +0.35, 0.0,  # left front leg (position control)
            0.0, -0.35, 0.0,  # right front leg (position control)
            0.0,  # front left leg (velocity control)
            0.0,  # front right leg (velocity control)
            0.0,  # rear left leg (velocity control)
            0.0,  # rear right leg (velocity control)
        ])

        self.pd_control_kp_real_robot = numpy.array([
            60.0, 60.0, 60.0,  # left rear leg (position control)
            60.0, 60.0, 60.0,  # right rear leg (position control)
            60.0, 60.0, 60.0,  # left front leg (position control)
            60.0, 60.0, 60.0,  # right front leg (position control)
        ])
        self.pd_control_kd_real_robot = numpy.array([
            3.0, 3.0, 3.0,  # left rear leg (position control)
            3.0, 3.0, 3.0,  # right rear leg (position control)
            3.0, 3.0, 3.0,  # left front leg (position control)
            3.0, 3.0, 3.0,  # right front leg (position control)
        ])

        # --------------------------------------------------------------------

        # change default position
        self.joint_default_position = \
            self.joint_default_position_real_robot_whole_body[self.index_of_joints_controlled].copy()
        self.joint_default_position_tensor = \
            torch.tensor(numpy.array([self.joint_default_position]), dtype=torch.float32)

        # change scales value
        self.nn_obs_scale_lin_vel = 1.00
        self.nn_obs_scale_ang_vel = 0.25
        self.nn_obs_scale_gravity = 1.00
        self.nn_obs_scale_dof_pos = 1.00
        self.nn_obs_scale_dof_vel = 0.10
        self.nn_obs_scale_action = 1.00
        self.nn_act_scale_action = 1.00

        self.nn_obs_scale_command = torch.tensor(numpy.array(
            [[self.nn_obs_scale_lin_vel,
              self.nn_obs_scale_lin_vel,
              self.nn_obs_scale_ang_vel]]
        ), dtype=torch.float)

        # --------------------------------------------------------------------
        # input

        # env
        self.num_envs = 1
        self.device = torch.device("cpu")

        # actor
        self.num_actor_obs = 53  # 观察量维度
        self.num_actor_obs_stack = 10  # 观察量堆栈深度
        self.num_actor_act = self.number_of_joint_controlled

        # flags
        self.flag_warmed_up = FlagState.CLEAR
        self.flag_buffer_inited = FlagState.CLEAR

        # commands
        self.commands = torch.zeros(self.num_envs, 3)

        """
        Jason 2024-12-25:
        指令信号一阶滤波器，主要过是让指令更加平滑
        """
        self.commands_filter_cutoff_frequency = 0.50  # Hz
        self.commands_filter_tau = 1 / (2 * numpy.pi * self.commands_filter_cutoff_frequency)
        self.commands_filter_alpha = self.commands_filter_tau \
                                     / (self.commands_filter_tau + (1 / self.control_frequency))

        self.commands_safety_ratio = 0.9
        self.command_linear_velocity_x_range = torch.tensor(numpy.array([[-0.50, 0.50]]), dtype=torch.float) \
                                               * self.commands_safety_ratio
        self.command_linear_velocity_y_range = torch.tensor(numpy.array([[-0.50, 0.50]]), dtype=torch.float) \
                                               * self.commands_safety_ratio
        self.command_angular_velocity_yaw_range = torch.tensor(numpy.array([[-1.00, 1.00]]), dtype=torch.float) \
                                                  * self.commands_safety_ratio

        self.measured_joint_position = torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.measured_joint_velocity = torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.measured_joint_position_offset = torch.zeros(self.num_envs, self.number_of_joint_controlled)

        self.gravity_vector = torch.tensor(numpy.array([[0.0, 0.0, -1.0]]), dtype=torch.float)
        self.base_quat_to_world = torch.tensor(numpy.array([[0.0, 0.0, 0.0, 1.0]]), dtype=torch.float)

        self.nn_actor = None

        # --------------------------------------------------------------------

        self._init_actor()

        # --------------------------------------------------------------------
        # gait
        self.num_feet = 4
        self.gait_cycle_period = 1.6  # unit: s
        self.gait_cycle_frequency = 1.0 / self.gait_cycle_period

        self.gait_generator = GaitGenerator(
            num_envs=self.num_envs,
            num_feet=self.num_feet,
            dt=(self.dt * self.decimation),
            frequency=self.gait_cycle_frequency,
            device=self.device,
        )

        self.required_time_of_flags_of_stand_command = self.gait_cycle_period * 1.5  # unit: s
        self.hold_time_of_flags_of_stand_command = torch.ones(self.num_envs) \
                                                   * self.required_time_of_flags_of_stand_command

        self.gait_patterns = [
            "stand", "walk",
        ]

        self.env_ids_of_stand_command = torch.arange(self.num_envs, dtype=torch.int, device=self.device, requires_grad=False)
        self.env_ids_of_walk_command = torch.arange(self.num_envs, dtype=torch.int, device=self.device, requires_grad=False)

        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # input
        self.base_xyz_vel_to_self = torch.zeros(self.num_envs, 3)
        self.base_rpy_vel_to_self = torch.zeros(self.num_envs, 3)
        self.base_xyz_to_world = torch.zeros(self.num_envs, 3)
        self.base_quat_to_world = torch.zeros(self.num_envs, 4)
        self.base_project_gravity = torch.zeros(self.num_envs, 3)
        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # output
        self.target_joint_position_offset = torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.target_joint_position = torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.target_joint_torque = torch.zeros(self.num_envs, self.number_of_joint_controlled)
        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # push reaction
        self.rest_time_of_push_reaction = torch.zeros(self.num_envs)
        # --------------------------------------------------------------------

    def _init_actor(self):
        self.nn_actor_input_commands = \
            torch.zeros(self.num_envs, 3)
        self.nn_actor_input_base_angular_velocity = \
            torch.zeros(self.num_envs, 3)
        self.nn_actor_input_base_projected_gravity = \
            torch.zeros(self.num_envs, 3)
        self.nn_actor_input_measured_joint_position_offset = \
            torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.nn_actor_input_measured_joint_velocity = \
            torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.nn_actor_input_action = \
            torch.zeros(self.num_envs, self.number_of_joint_controlled)
        self.nn_actor_input_gait_x = \
            torch.zeros(self.num_envs, 2)
        self.nn_actor_input_gait_y = \
            torch.zeros(self.num_envs, 2)
        self.nn_actor_input_length = \
            self.num_actor_obs * self.num_actor_obs_stack
        self.nn_actor_input = \
            torch.zeros(self.num_envs, self.nn_actor_input_length)

        self.nn_actor_output_tensor = \
            torch.zeros(self.num_envs, self.num_actor_act)
        self.nn_actor_output_raw = \
            torch.zeros(self.num_envs, self.num_actor_act)
        self.nn_actor_output = \
            torch.zeros(self.num_envs, self.num_actor_act)
        self.nn_actor_output_scale = \
            torch.ones(self.num_envs, self.num_actor_act) \
            * self.nn_act_scale_action
        self.nn_actor_output_clip_min = \
            torch.tensor([
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
            ])
        self.nn_actor_output_clip_max = \
            torch.tensor([
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
            ])
        self.nn_actor_output_scaled = torch.tensor([])

        """
        Jason 2025-12-29:
        Considering the parallel ankle joint, limit the output joint position range.
        """
        self.target_joint_position_clip_min = \
            torch.tensor([
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
                -5.0, -5.0, -5.0,
            ])
        self.target_joint_position_clip_max = \
            torch.tensor([
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
                +5.0, +5.0, +5.0,
            ])

    def _load_actor(self):
        if self.nn_actor is None:
            if self.actor_model_file_path is None:
                model_file_path = os.path.join(
                    gl_resource.path,
                    "locomotion",
                    "hxc_leg_body_rl_walk_cpg.pt"
                )
            else:
                model_file_path = self.actor_model_file_path

            try:
                self.nn_actor = torch.jit.load(model_file_path, map_location=self.device)
            except Exception as exp:
                Logger().print_error(f"Load actor model error: {exp}")
                self.nn_actor = None

            """
            2026-02-28:
            模型加载完成后，设置为评估模式，并使用 torch.jit.optimize_for_inference 进行优化，以提高推理效率。
            """
            self.nn_actor.eval()
            self.nn_actor = torch.jit.optimize_for_inference(self.nn_actor)

    def _init_buffer(self, init_output):
        """"""
        """
        Jason 2024-07-07:
        If the init_output is the default position, the nn_actor_output will be zero
        
        epsilon to avoid zero division
        """
        epsilon = 1e-8
        self.nn_actor_output = \
            (init_output - self.joint_default_position_tensor) / (self.nn_actor_output_scale + epsilon)

    def _update_buffer(
            self,
            commands,
            base_measured_quat_to_world,
            base_measured_rpy_vel_to_self,
            joint_measured_position,
            joint_measured_velocity,
    ):
        # update commands
        self.commands = \
            self._commands_filter(commands)

        # clip commands
        self.commands[0, 0] = torch.clip(
            self.commands[0, 0],
            min=self.command_linear_velocity_x_range[0, 0],
            max=self.command_linear_velocity_x_range[0, 1],
        )
        self.commands[0, 1] = torch.clip(
            self.commands[0, 1],
            min=self.command_linear_velocity_y_range[0, 0],
            max=self.command_linear_velocity_y_range[0, 1],
        )
        self.commands[0, 2] = torch.clip(
            self.commands[0, 2],
            min=self.command_angular_velocity_yaw_range[0, 0],
            max=self.command_angular_velocity_yaw_range[0, 1],
        )

        # Jason 2024-07-08:
        # torch_quat_rotate_inverse will be called here at first and finish the torch.jit.script
        self.base_quat_to_world = base_measured_quat_to_world
        self.base_project_gravity = torch_quat_rotate_inverse(self.base_quat_to_world, self.gravity_vector)

        self.base_rpy_vel_to_self = base_measured_rpy_vel_to_self

        self.measured_joint_position = joint_measured_position
        self.measured_joint_position_offset = self.measured_joint_position - self.joint_default_position_tensor

        self.measured_joint_velocity = joint_measured_velocity

    def _actor_ready(self):
        # create stacked obs
        for i in range(self.num_actor_obs_stack):
            # prepare
            self._actor_prepare()

            # obs
            self._actor_obs()

        # nn
        self._actor_nn()

        # output
        self._actor_output()

        return self.target_joint_position

    def _actor_run(self):
        # prepare
        self._actor_prepare()

        # obs
        self._actor_obs()

        # nn
        self._actor_nn()

        # output
        self._actor_output()

        return self.target_joint_position

    def _actor_prepare(self):
        # commands
        self.nn_actor_input_commands = self.commands

        # base angular velocity
        self.nn_actor_input_base_angular_velocity = self.base_rpy_vel_to_self

        # projected gravity
        self.nn_actor_input_base_projected_gravity = self.base_project_gravity

        # measured joint position offset, velocity
        self.nn_actor_input_measured_joint_position_offset = self.measured_joint_position_offset
        self.nn_actor_input_measured_joint_velocity = self.measured_joint_velocity

        # actions
        self.nn_actor_input_action = self.nn_actor_output.clone()

        # gait x, y
        self.nn_actor_input_gait_x = self.gait_generator.get_x_norm()
        self.nn_actor_input_gait_y = self.gait_generator.get_y_norm()

    def _actor_obs(self):
        components = [
            ('commands', self.nn_actor_input_commands, self.nn_obs_scale_command),
            ('base_angular_velocity', self.nn_actor_input_base_angular_velocity, self.nn_obs_scale_ang_vel),
            ('base_projected_gravity', self.nn_actor_input_base_projected_gravity, self.nn_obs_scale_gravity),
            ('measured_joint_position_offset', self.nn_actor_input_measured_joint_position_offset, self.nn_obs_scale_dof_pos),
            ('measured_joint_velocity', self.nn_actor_input_measured_joint_velocity, self.nn_obs_scale_dof_vel),
            ('action', self.nn_actor_input_action, self.nn_obs_scale_action),
            ('gait_x', self.nn_actor_input_gait_x, 1.0),
            ('gait_y', self.nn_actor_input_gait_y, 1.0),
        ]

        start_index = 0
        concatenated_inputs = []

        for name, component, scale in components:
            comp_len = component.shape[1]
            start_index = start_index + comp_len
            end_index = start_index + comp_len * (self.num_actor_obs_stack - 1)
            history_values = self.nn_actor_input[:, start_index:end_index]
            current_input = component * scale
            concatenated_inputs.extend([history_values, current_input])

            start_index += comp_len * (self.num_actor_obs_stack - 1)

        self.nn_actor_input = torch.cat(concatenated_inputs, dim=-1).float()

    def _actor_nn(self):
        self.nn_actor_output_tensor = self.nn_actor(self.nn_actor_input)

        self.nn_actor_output_raw = self.nn_actor_output_tensor.detach()

        self.nn_actor_output = torch.clip(
            self.nn_actor_output_raw,
            min=self.nn_actor_output_clip_min,
            max=self.nn_actor_output_clip_max
        )

    def _actor_output(self):
        self.target_joint_position_offset = \
            self.nn_actor_output * self.nn_actor_output_scale

        self.target_joint_position = \
            self.target_joint_position_offset + self.joint_default_position_tensor

        self.target_joint_position = torch.clip(
            self.target_joint_position,
            min=self.target_joint_position_clip_min,
            max=self.target_joint_position_clip_max,
        )

    def _commands_filter(
            self,
            commands
    ):
        """"""
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

        # set too small value to zero
        self.commands = torch.where(
            torch.abs(self.commands) < 0.0001,
            torch.zeros_like(self.commands),
            self.commands,
        )

        return self.commands

    def _commands_refinement(
            self,
            commands,
    ):
        # if belong to stand command, set all commands to zero
        self.flags_of_stand_command = torch.zeros(self.num_envs, dtype=torch.bool)
        self.flags_of_stand_command[self.env_ids_of_stand_command] = True

        commands = torch.where(
            self.flags_of_stand_command,
            torch.zeros_like(commands),
            commands,
        )

        return commands

    def update_flags_of_stand_command(
            self,
            commands,
    ):
        """
        Get the flags of stand command.

        Input:
        - commands: commands for the robot, [linear_velocity_x, linear_velocity_y, angular_velocity], m/s, m/s, rad/s

        Output:
        - flags_of_stand_command: flags of stand command

        Description:
        - situation 1: the norm of the first two elements of the command is less than 0.1
        - situation 2: the value of the third element of the command is less than 0.1
        - hold_time_of_flags_of_stand_command: hold time of flags_of_stand_command, self.gait_cycle_period / 2
        """
        # situation 1: the norm of the first two elements of the command is less than 0.10
        flags_of_stand_command_s1 = torch.norm(commands[:, :2], dim=1) <= 0.10  # dim 2->1

        # situation 2: the value of the third element of the command is less than 0.10
        flags_of_stand_command_s2 = torch.abs(commands[:, 2]) <= 0.10  # dim 1

        # situation 1 and situation 2
        flags_of_stand_command = flags_of_stand_command_s1 * flags_of_stand_command_s2
        flags_of_stand_command = flags_of_stand_command.bool()

        # calculate the hold time of flags_of_stand_command
        self.hold_time_of_flags_of_stand_command += flags_of_stand_command * (self.dt * self.decimation)
        self.hold_time_of_flags_of_stand_command *= flags_of_stand_command
        self.hold_time_of_flags_of_stand_command = torch.clip(
            self.hold_time_of_flags_of_stand_command,
            min=0.0,
            max=self.required_time_of_flags_of_stand_command,
        )

        flags_of_stand_command = \
            torch.where(self.hold_time_of_flags_of_stand_command
                        >= self.required_time_of_flags_of_stand_command,
                        True,
                        False)

        return flags_of_stand_command

    def update_flags_of_walk_command(
            self,
            commands,
    ):
        """
        Get the flags of walk command.

        Input:
        - commands: commands for the robot, [linear_velocity_x, linear_velocity_y, angular_velocity], m/s, m/s, rad/s

        Output:
        - flags_of_walk_command: flags of walk command

        Description:
        - situation 1: the norm of the first two elements of the command is greater than 0.1
        - situation 2: the value of the third element of the command is greater than 0.1
        """
        # situation 1: the norm of the first two elements of the command is greater than 0.10
        flags_of_walk_command_s1 = torch.norm(commands[:, :2], dim=1) > 0.10  # dim 2->1

        # situation 2: the value of the third element of the command is greater than 0.10
        flags_of_walk_command_s2 = torch.abs(commands[:, 2]) > 0.10  # dim 1

        # situation 1 or situation 2
        flags_of_walk_command = flags_of_walk_command_s1 + flags_of_walk_command_s2
        flags_of_walk_command = flags_of_walk_command.bool()

        return flags_of_walk_command

    def _update_gait_generator_pattern(
            self,
            commands,
    ):
        """
        Update the gait generator pattern.

        Input:
        - commands: commands for the robot, [linear_velocity_x, linear_velocity_y, angular_velocity], m/s, m/s, rad/s
        """
        env_ids_of_stand_command = torch.Tensor([]).int().to(self.device)
        env_ids_of_walk_command = torch.Tensor([]).int().to(self.device)

        if "stand" in self.gait_patterns:
            env_ids_of_stand_command = torch.where(self.update_flags_of_stand_command(commands))[0]

        if "walk" in self.gait_patterns:
            env_ids_of_walk_command = torch.where(self.update_flags_of_walk_command(commands))[0]

        self.env_ids_of_stand_command = env_ids_of_stand_command
        self.env_ids_of_walk_command = env_ids_of_walk_command

        self.gait_generator.set_pattern(pattern="stand", env_ids=self.env_ids_of_stand_command)
        self.gait_generator.set_pattern(pattern="walk", env_ids=self.env_ids_of_walk_command)

    def _gait_pattern_refinement(
            self,
            commands,
            base_measured_quat_to_world,
            base_measured_rpy_vel_to_self,
            joint_measured_position,
            joint_measured_velocity,
    ):
        """
        Refine the gait pattern.

        Input:
        - commands: commands for the robot, [linear_velocity_x, linear_velocity_y, angular_velocity], m/s, m/s, rad/s
        - base_measured_quat_to_world: measured base quaternion to world, [x, y, z, w]
        - base_measured_rpy_vel_to_self: measured base angular velocity in world, [roll, pitch, yaw], rad/s
        - joint_measured_position: measured joint position in URDF, rad
        - joint_measured_velocity: measured joint velocity in URDF, rad/s
        """
        pass

    def run(
            self,
            joint_measured_position,
            joint_measured_velocity,
            init_output=None,
            commands=numpy.array([0, 0, 0]),
            base_measured_quat_to_world=numpy.array([0, 0, 0, 1]),
            base_measured_rpy_vel_to_self=numpy.array([0, 0, 0]),
            **kwargs,
    ):
        """
        Run the RL walk control algorithm.

        Input:
        - joint_measured_position: measured joint position in URDF, rad
        - joint_measured_velocity: measured joint velocity in URDF, rad/s
        - init_output: initial output of the robot, rad
        - commands: commands for the robot, [linear_velocity_x, linear_velocity_y, angular_velocity], m/s, m/s, rad/s
        - base_measured_quat_to_world: measured base quaternion to world, [x, y, z, w]
        - base_measured_rpy_vel_to_self: measured base angular velocity in world, [roll, pitch, yaw], rad/s

        Output:
        - target_joint_position: output joint control target, rad
        """

        if self.stage == AlgorithmStage.STAGE_INIT:
            # reset flags
            self.flag_warmed_up = FlagState.CLEAR
            self.flag_buffer_inited = FlagState.CLEAR

            # reset gait generator
            self.gait_generator.reset()

            # reset decimation count
            self.decimation_count = 0

            self.stage = AlgorithmStage.STAGE_WARM_UP

        if self.stage == AlgorithmStage.STAGE_START:
            # reset decimation count
            self.decimation_count = 0

            self.stage = AlgorithmStage.STAGE_WARM_UP

        if self.stage == AlgorithmStage.STAGE_WARM_UP and self.flag_warmed_up == FlagState.CLEAR:
            # run neural network to warm up, all inputs are zero
            self._load_actor()

            self.nn_actor(self.nn_actor_input)

            if self.warmup_start_time is None:
                self.warmup_start_time = time.time()

            if time.time() - self.warmup_start_time >= self.warmup_period:
                self._init_actor()

                # set flags
                self.flag_warmed_up = FlagState.SET

                self.stage = AlgorithmStage.STAGE_RUN
                Logger().print_info("Warmup done. Running algorithm...")

            # FIXME: must use clone() to avoid the target_joint_position be changed outside
            self.target_joint_position = self.joint_default_position_tensor.clone()
            target_joint_position = self.target_joint_position
            target_joint_position = target_joint_position.numpy()[0]

            return target_joint_position

        # check decimation count
        if self.decimation_count % self.decimation == 0:
            # clear decimation count
            self.decimation_count = 0

            # update decimation count
            self.decimation_count += 1
        else:
            # update decimation count
            self.decimation_count += 1

            target_joint_position = self.target_joint_position
            target_joint_position = target_joint_position.numpy()[0]

            return target_joint_position

        # --------------------------------------------------------------------
        # numpy.array -> torch.tensor
        # Jason 2024-07-07: torch.from_numpy() share the same memory with numpy array, will not copy the data
        if init_output is None:
            init_output = numpy.zeros(self.number_of_joint_controlled)

        torch_init_output = \
            torch.from_numpy(init_output.astype(numpy.float32)).unsqueeze(0)
        torch_commands = \
            torch.from_numpy(commands.astype(numpy.float32)).unsqueeze(0)
        torch_base_measured_quat_to_world = \
            torch.from_numpy(base_measured_quat_to_world.astype(numpy.float32)).unsqueeze(0)
        torch_base_measured_rpy_vel_to_self = \
            torch.from_numpy(base_measured_rpy_vel_to_self.astype(numpy.float32)).unsqueeze(0)
        torch_joint_measured_position = \
            torch.from_numpy(joint_measured_position.astype(numpy.float32)).unsqueeze(0)
        torch_joint_measured_velocity = \
            torch.from_numpy(joint_measured_velocity.astype(numpy.float32)).unsqueeze(0)

        # --------------------------------------------------------------------
        # gait
        self.gait_generator.step()

        self._gait_pattern_refinement(
            commands=torch_commands,
            base_measured_quat_to_world=torch_base_measured_quat_to_world,
            base_measured_rpy_vel_to_self=torch_base_measured_rpy_vel_to_self,
            joint_measured_position=torch_joint_measured_position,
            joint_measured_velocity=torch_joint_measured_velocity,
        )

        self._update_gait_generator_pattern(
            commands=torch_commands,
        )

        torch_commands = self._commands_refinement(
            commands=torch_commands,
        )

        # --------------------------------------------------------------------
        # state
        if self.flag_buffer_inited == FlagState.CLEAR:
            self._init_buffer(
                init_output=torch_init_output,
            )
            self._update_buffer(
                commands=torch_commands,
                base_measured_quat_to_world=torch_base_measured_quat_to_world,
                base_measured_rpy_vel_to_self=torch_base_measured_rpy_vel_to_self,
                joint_measured_position=torch_joint_measured_position,
                joint_measured_velocity=torch_joint_measured_velocity,
            )

            # actor
            target_joint_position = self._actor_ready()  # Jason 2024-12-10: 预备

            # flag
            self.flag_buffer_inited = FlagState.SET

        else:
            self._update_buffer(
                commands=torch_commands,
                base_measured_quat_to_world=torch_base_measured_quat_to_world,
                base_measured_rpy_vel_to_self=torch_base_measured_rpy_vel_to_self,
                joint_measured_position=torch_joint_measured_position,
                joint_measured_velocity=torch_joint_measured_velocity,
            )

            # actor
            target_joint_position = self._actor_run()  # Jason 2024-12-10: 跑！！！

        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # output
        target_joint_position = target_joint_position.numpy()[0]

        # --------------------------------------------------------------------

        return target_joint_position
