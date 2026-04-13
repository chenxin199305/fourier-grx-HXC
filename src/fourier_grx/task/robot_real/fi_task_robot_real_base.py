from fourier_core.predefine import *

from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.robot_real.fi_algorithm_robot_real_base import (
    AlgorithmRobotRealBaseControlModel,
)


class TaskRobotRealBase(TaskBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmRobotRealBaseControlModel()
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS
