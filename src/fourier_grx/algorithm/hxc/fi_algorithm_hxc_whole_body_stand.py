import numpy

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_grx.predefine import *
from fourier_grx.algorithm.hxc.fi_algorithm_hxc_whole_body import (
    AlgorithmHXCWholeBodyControlModel,
)


class AlgorithmHXCWholeBodyStandControlModel(AlgorithmHXCWholeBodyControlModel):
    def __init__(
            self,
            dt=0.02,
            motion_period=2.0,
    ):
        super().__init__()

        # --------------------------------------------------
        # dt and other parameters
        self.control_frequency: float = 50.0
        self.dt: float = dt
        self.decimation: int = int((1 / self.control_frequency) / self.dt)
        self.decimation_count = 0

        # --------------------------------------------------

        """
        Move robot to stand position in motion period
        """
        self.motion_period = motion_period  # unit : s
        self.motion_dt = self.decimation * self.dt
        self.motion_t = 0
        self.motion_ratio = 0

        self.target_velocity = 0.0
        self.target_direction = 0.0

        self.joint_start_position = numpy.zeros(self.number_of_joint)
        self.joint_target_position = self.joint_default_position_real_robot_whole_body.copy()

        self.output_work_space = RobotWorkSpace.NONE

        self.output_joint_control_mode = numpy.zeros(self.number_of_joint)
        self.output_joint_position = numpy.zeros(self.number_of_joint)

    def run(
            self,
            joint_measured_position,  # rad
    ):
        """
        Input:
        joint_measured_position: measured joint position in URDF, rad

        Output:
        work_space: work space of output joint control target
        control_mode: control mode of output joint control target
        joint_pd_control_target: output joint control target, rad
        """

        # use measured position as default pd target
        work_space = RobotWorkSpace.NONE
        control_mode = JointControlMode.NONE \
                       * numpy.ones(self.number_of_joint)
        joint_pd_control_target = joint_measured_position

        # --------------------------------------------------

        # check decimation count
        if self.decimation_count % self.decimation == 0:
            # clear decimation count
            self.decimation_count = 0

            # update decimation count
            self.decimation_count += 1
        else:
            # update decimation count
            self.decimation_count += 1

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

            return work_space, control_mode, joint_pd_control_target

        # --------------------------------------------------

        if self.stage == AlgorithmStage.STAGE_INIT:
            pass

            # update algorithm stage
            self.stage = AlgorithmStage.STAGE_START

        elif self.stage == AlgorithmStage.STAGE_START:
            # reset t
            self.motion_t = 0

            # reset start position
            self.joint_start_position = joint_measured_position

            self.output_work_space = RobotWorkSpace.JOINT_SPACE
            self.output_joint_control_mode = JointControlMode.PD * \
                                             numpy.ones(self.number_of_joint)
            self.output_joint_position = numpy.zeros(self.number_of_joint)

            # move to start position
            self.output_joint_position = self.joint_start_position

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

            # update algorithm stage
            self.stage = AlgorithmStage.STAGE_PROCESS_01

        elif self.stage == AlgorithmStage.STAGE_PROCESS_01:
            # update ratio
            self.motion_ratio = self.motion_t / self.motion_period

            self.output_work_space = RobotWorkSpace.JOINT_SPACE
            self.output_joint_control_mode = JointControlMode.PD * \
                                             numpy.ones(self.number_of_joint)
            self.output_joint_position = numpy.zeros(self.number_of_joint)

            # move from start position to target position
            self.output_joint_position = (
                    self.joint_start_position
                    + (self.joint_target_position
                       - self.joint_start_position)
                    * self.motion_ratio
            )

            # add dt
            self.motion_t += self.motion_dt

            if self.motion_t > self.motion_period:
                self.motion_t = self.motion_period

                # update algorithm stage
                self.stage = AlgorithmStage.STAGE_PROCESS_02

            Logger().print_info(
                f"motion_ratio = "
                f"{round(self.motion_ratio * 100, 1)}%"
            )

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

        elif self.stage == AlgorithmStage.STAGE_PROCESS_02:
            self.output_work_space = RobotWorkSpace.JOINT_SPACE
            self.output_joint_control_mode = JointControlMode.PD * \
                                             numpy.ones(self.number_of_joint)
            self.output_joint_position = self.joint_target_position.copy()

            Logger().print_info(
                f"motion_ratio = 100.0% "
                f"Algorithm Finish!"
            )

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

            # update algorithm stage
            self.stage = AlgorithmStage.STAGE_FINISH

        elif self.stage == AlgorithmStage.STAGE_FINISH:
            # do not change anything

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

        else:
            self.stage = AlgorithmStage.STAGE_START

            # output
            work_space = self.output_work_space
            control_mode = self.output_joint_control_mode
            joint_pd_control_target = self.output_joint_position

        return work_space, control_mode, joint_pd_control_target
