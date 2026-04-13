from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.hxc import (
    AlgorithmHXCIdleControlModel,
)
from fourier_grx.task.hxc.fi_task_hxc_base import (
    TaskHXCBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.HXCT1,
)
class TaskHXCIdle(TaskHXCBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmHXCIdleControlModel()
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def function_on_activate(self, **kwargs) -> FunctionResult:
        """
        This function is called when the task starts.
        """
        # Jason 2025-07-01: Must be implemented to overwrite the base class method.
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

    # =====================================================================================================
