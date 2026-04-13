import time

from fourier_grx.algorithm.robot_real.fi_algorithm_robot_real_base import (
    AlgorithmRobotRealBaseControlModel,
)


class AlgorithmRobotRealWaitControlModel(AlgorithmRobotRealBaseControlModel):
    def __init__(self):
        super().__init__()

        self.wait_duration = 3.0  # unit : s
        self.wait_start_time = 0.0

    def run(self, **kwargs):
        pass
