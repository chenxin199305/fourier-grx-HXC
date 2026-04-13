from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.robot_base.fi_algorithm_robot_base_idle import (
    AlgorithmRobotBaseIdleControlModel,
)
from fourier_grx.task.robot_base.fi_task_robot_base_base import (
    TaskRobotBaseBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.Base,
)
class TaskRobotBaseIdle(TaskRobotBaseBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmRobotBaseIdleControlModel()
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def function_component(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS

    def function_standalone(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS
