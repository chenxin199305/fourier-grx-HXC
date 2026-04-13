import numpy

from fourier_core.predefine import *

from fourier_grx.robot.hxc.fi_robot_hxc_param import (
    RobotHXCParam,
)
from fourier_grx.algorithm.fi_algorithm_base import (
    AlgorithmBaseControlModel,
)


class AlgorithmHXCBaseControlModel(AlgorithmBaseControlModel):
    def __init__(self):
        """
        HXC Base Control Model
        """

        super().__init__()

        # --------------------------------------------------------------------
        # for real robot

        self.number_of_joint_whole_body = RobotHXCParam.number_of_joint
        self.pd_control_kp_real_robot_whole_body = RobotHXCParam.joint_pd_control_kp
        self.pd_control_kd_real_robot_whole_body = RobotHXCParam.joint_pd_control_kd

        self.control_mode_real_robot_whole_body = \
            [JointControlMode.PD] * self.number_of_joint_whole_body
        # wheel joints are velocity-controlled; override their default
        for i in RobotHXCParam.indexes_of_wheel_body_joints:
            self.control_mode_real_robot_whole_body[i] = JointControlMode.VELOCITY

        self.joint_default_position_real_robot_whole_body = numpy.zeros(self.number_of_joint_whole_body)
        self.joint_default_velocity_real_robot_whole_body = numpy.zeros(self.number_of_joint_whole_body)

        # --------------------------------------------------------------------

        self.number_of_actuator = self.number_of_joint_whole_body
        self.number_of_joint = self.number_of_joint_whole_body

        self.index_of_actuators_real_robot = numpy.arange(self.number_of_actuator)
        self.index_of_joints_real_robot = numpy.arange(self.number_of_joint)

        self.pd_control_kp_real_robot = \
            self.pd_control_kp_real_robot_whole_body[self.index_of_joints_real_robot].copy()
        self.pd_control_kd_real_robot = \
            self.pd_control_kd_real_robot_whole_body[self.index_of_joints_real_robot].copy()

        # --------------------------------------------------------------------

        self.number_of_joint_controlled = self.number_of_joint_whole_body

        self.index_of_joints_controlled = numpy.arange(self.number_of_joint_controlled)

        self.joint_default_position = numpy.zeros(self.number_of_joint_controlled)

        # --------------------------------------------------------------------
