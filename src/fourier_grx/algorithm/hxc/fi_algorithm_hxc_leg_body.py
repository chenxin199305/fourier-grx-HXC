import numpy

from fourier_grx.algorithm.hxc.fi_algorithm_hxc_base import (
    AlgorithmHXCBaseControlModel,
)


class AlgorithmHXCLegBodyControlModel(AlgorithmHXCBaseControlModel):
    def __init__(self):
        super().__init__()

        # --------------------------------------------------------------------
        # for real robot

        self.number_of_actuator = 3 + 3 + 3 + 3
        self.number_of_joint = 3 + 3 + 3 + 3

        self.index_of_actuators_real_robot = numpy.array([
            0, 1, 2,  # front left leg (position control)
            3, 4, 5,  # front right leg (position control)
            6, 7, 8,  # rear left leg (position control)
            9, 10, 11,  # rear right leg (position control)
        ])
        self.index_of_joints_real_robot = numpy.array([
            0, 1, 2,  # front left leg (position control)
            3, 4, 5,  # front right leg (position control)
            6, 7, 8,  # rear left leg (position control)
            9, 10, 11,  # rear right leg (position control)
        ])

        self.pd_control_kp_real_robot = \
            self.pd_control_kp_real_robot_whole_body[self.index_of_joints_real_robot].copy()
        self.pd_control_kd_real_robot = \
            self.pd_control_kd_real_robot_whole_body[self.index_of_joints_real_robot].copy()

        # --------------------------------------------------------------------

        self.number_of_joint_controlled = self.number_of_joint

        self.index_of_joints_controlled = self.index_of_joints_real_robot.copy()

        self.joint_default_position = \
            self.joint_default_position_real_robot_whole_body[self.index_of_joints_controlled].copy()

        # --------------------------------------------------------------------
