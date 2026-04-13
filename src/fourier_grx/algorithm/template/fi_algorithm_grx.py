import numpy

from fourier_grx.algorithm.fi_algorithm_base import AlgorithmBase


class AlgorithmGRX(AlgorithmBase):
    def __init__(self):
        super().__init__()

        # --------------------------------------------------------------------
        # for real robot
        self.number_of_joint = 5 + 5

        self.index_of_joints_real_robot = numpy.array([
            0, 1, 2, 3, 4,  # 5 # left leg (5), no ankle roll
            6, 7, 8, 9, 10,  # 11 # right leg (5), no ankle roll
        ])
        self.pd_control_kp_real_robot = numpy.array([
            60, 45, 130, 130, 16,  # left leg(5)
            60, 45, 130, 130, 16,  # right leg(5)
        ]) / (45 / 180 * numpy.pi)
        self.pd_control_kd_real_robot = \
            self.pd_control_kp_real_robot / 10 * 2.5
        # --------------------------------------------------------------------

    def run(self,
            algorithm_input=None):
        algorithm_output = None

        return algorithm_output
