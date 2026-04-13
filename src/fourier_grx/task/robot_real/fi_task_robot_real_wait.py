import time

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.robot_real.fi_algorithm_robot_real_wait import (
    AlgorithmRobotRealWaitControlModel,
)
from fourier_grx.task.robot_real.fi_task_robot_real_base import (
    TaskRobotRealBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.Base,
)
class TaskRobotRealWait(TaskRobotRealBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.

        Waits for task_model.wait_duration seconds, then finishes.
        Override wait_duration after calling register() to customise the delay.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmRobotRealWaitControlModel()
        self.task_key = TaskMenuRobotReal.TASK_WAIT

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:

        if self.task_model.stage == AlgorithmStage.STAGE_INIT:
            self.task_model.stage = AlgorithmStage.STAGE_START

        elif self.task_model.stage == AlgorithmStage.STAGE_START:
            Logger().print_info(
                f"{self.__class__.__name__}: waiting {self.task_model.wait_duration} seconds..."
            )
            self.task_model.wait_start_time = time.time()

            self.task_model.stage = AlgorithmStage.STAGE_PROCESS_01

        elif self.task_model.stage == AlgorithmStage.STAGE_PROCESS_01:
            elapsed = time.time() - self.task_model.wait_start_time
            if elapsed >= self.task_model.wait_duration:
                Logger().print_info(
                    f"{self.__class__.__name__}: wait complete "
                    f"({self.task_model.wait_duration} s elapsed)."
                )
                self.task_model.stage = AlgorithmStage.STAGE_FINISH

        elif self.task_model.stage == AlgorithmStage.STAGE_FINISH:
            self.task_model.stage = AlgorithmStage.STAGE_SWITCH

        elif self.task_model.stage == AlgorithmStage.STAGE_SWITCH:
            from fourier_grx.robot.robot_base.fi_robot_base import RobotBase
            robot: RobotBase = self.fsm_manager
            robot.set_task_command(task_command=TaskMenuRobotBase.TASK_IDLE)

        else:
            self.task_model.stage = AlgorithmStage.STAGE_INIT

        return FunctionResult.SUCCESS

    def function_component(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS

    def function_standalone(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS
