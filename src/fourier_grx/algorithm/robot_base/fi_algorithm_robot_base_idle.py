from fourier_grx.algorithm.robot_base.fi_algorithm_robot_base_base import (
    AlgorithmRobotBaseBaseControlModel,
)


class AlgorithmRobotBaseIdleControlModel(AlgorithmRobotBaseBaseControlModel):
    def __init__(self):
        super().__init__()

    def run(self, **kwargs):
        pass
