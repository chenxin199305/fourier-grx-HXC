import numpy
import torch

from fourier_grx.algorithm.hxc.fi_algorithm_hxc_whole_body import (
    AlgorithmHXCWholeBodyControlModel,
)
from fourier_grx.predefine import AlgorithmStage
from fourier_grx.robot.hxc.fi_robot_hxc_param import RobotHXCParam


class AlgorithmHXCWholeBodySteerDriveControlModel(AlgorithmHXCWholeBodyControlModel):
    def __init__(
            self,
            dt: float = 0.02,
            motion_period: float = 2.0,
    ):
        super().__init__()

        self.control_frequency: float = 50.0
        self.dt: float = dt
        self.decimation: int = max(1, int((1 / self.control_frequency) / self.dt))
        self.decimation_count = 0

        self.motion_period = motion_period
        self.motion_dt = self.decimation * self.dt
        self.motion_t = 0.0

        self.command_steering_angle_range = torch.tensor([[-0.70, 0.70]], dtype=torch.float)
        self.command_wheel_velocity_range = torch.tensor([[-2*numpy.pi, 2*numpy.pi]], dtype=torch.float)

        self.steering_joint_indices = numpy.array([2, 5, 8, 11], dtype=int)
        self.wheel_joint_indices = RobotHXCParam.indexes_of_wheel_body_joints.copy()
        self.wheel_joint_direction = numpy.array([+1, -1, +1, -1], dtype=int)

        self.joint_default_position_real_robot_whole_body = numpy.array([
            0.0, 0.0, +0.7854,  # front left leg
            0.0, 0.0, -0.7854,  # front right leg
            0.0, 0.0, -0.7854,  # rear left leg
            0.0, 0.0, +0.7854,  # rear right leg
            0.0,  # front left wheel
            0.0,  # front right wheel
            0.0,  # rear left wheel
            0.0,  # rear right wheel
        ])

        self.joint_default_position = \
            self.joint_default_position_real_robot_whole_body[self.index_of_joints_controlled].copy()
        self.steering_joint_default_position = \
            self.joint_default_position[self.steering_joint_indices].copy()

        self.joint_start_position = numpy.zeros(self.number_of_joint)
        self.output_joint_position = numpy.zeros(self.number_of_joint)
        self.output_joint_velocity = numpy.zeros(self.number_of_joint)

    def _clip_steering_angle(self, steering_angle: float) -> float:
        return float(numpy.clip(
            steering_angle,
            self.command_steering_angle_range[0, 0].item(),
            self.command_steering_angle_range[0, 1].item(),
        ))

    def _clip_wheel_velocity(self, wheel_velocity: float) -> float:
        return float(numpy.clip(
            wheel_velocity,
            self.command_wheel_velocity_range[0, 0].item(),
            self.command_wheel_velocity_range[0, 1].item(),
        ))

    def _build_joint_target_position(self, steering_angle: float) -> numpy.ndarray:
        joint_target_position = self.joint_default_position.copy()
        joint_target_position[self.steering_joint_indices] = (
            self.steering_joint_default_position + steering_angle
        )
        return joint_target_position

    def _build_joint_target_velocity(self, wheel_velocity: float) -> numpy.ndarray:
        joint_target_velocity = numpy.zeros(self.number_of_joint)
        joint_target_velocity[self.wheel_joint_indices] = wheel_velocity * self.wheel_joint_direction
        return joint_target_velocity

    def run(  # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            joint_measured_position,
            steering_angle=0.0,
            wheel_velocity=0.0,
            **kwargs,
    ):
        steering_angle = self._clip_steering_angle(steering_angle)
        wheel_velocity = self._clip_wheel_velocity(wheel_velocity)

        joint_target_position = self._build_joint_target_position(steering_angle=steering_angle)
        joint_target_velocity = self._build_joint_target_velocity(wheel_velocity=wheel_velocity)

        if self.decimation_count % self.decimation == 0:
            self.decimation_count = 1
        else:
            self.decimation_count += 1
            return self.output_joint_position, self.output_joint_velocity

        if self.stage == AlgorithmStage.STAGE_INIT:
            self.stage = AlgorithmStage.STAGE_START

        if self.stage == AlgorithmStage.STAGE_START:
            self.motion_t = 0.0
            self.joint_start_position = joint_measured_position.copy()
            self.output_joint_position = self.joint_start_position.copy()
            self.output_joint_velocity = numpy.zeros(self.number_of_joint)
            self.stage = AlgorithmStage.STAGE_PROCESS_01
            return self.output_joint_position, self.output_joint_velocity

        if self.stage == AlgorithmStage.STAGE_PROCESS_01:
            motion_ratio = self.motion_t / self.motion_period if self.motion_period > 0.0 else 1.0
            motion_ratio = float(numpy.clip(motion_ratio, 0.0, 1.0))

            self.output_joint_position = (
                self.joint_start_position
                + (joint_target_position - self.joint_start_position) * motion_ratio
            )
            self.output_joint_velocity = numpy.zeros(self.number_of_joint)

            self.motion_t += self.motion_dt
            if self.motion_t >= self.motion_period:
                self.motion_t = self.motion_period
                self.stage = AlgorithmStage.STAGE_FINISH

            return self.output_joint_position, self.output_joint_velocity

        self.output_joint_position = joint_target_position
        self.output_joint_velocity = joint_target_velocity

        return self.output_joint_position, self.output_joint_velocity
