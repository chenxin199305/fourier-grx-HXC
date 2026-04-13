from fourier_core.predefine import *

from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.robot_base.fi_algorithm_robot_base_base import (
    AlgorithmRobotBaseBaseControlModel,
)


class TaskRobotBaseBase(TaskBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmRobotBaseBaseControlModel()
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS
