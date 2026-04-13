from enum import Enum
from typing import Any
from collections.abc import Callable

from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.task.fi_task_base import (
    TaskBase,
)


class TaskTemplate(TaskBase):
    def __init__(
            self,
            fsm_manager: FSMManager,
            task_type: TaskFunctionType = TaskFunctionType.STANDALONE,
            register: bool = True,
            add_task: bool = True,
    ) -> None:
        """
        Initialize the task.

        Args:
            fsm_manager: The task manager.
            task_type: The type of the task.
            register: Whether to register the task to the fsm_manager. (let task know the fsm_manager)
            add_task: Whether to add the task to the fsm_manager. (let fsm_manager know the task)
        """
        super().__init__()

        if fsm_manager is None:
            raise ValueError("fsm_manager is None")

        self.fsm_manager: FSMManager | None = None
        self.task_key: Enum | None = None
        self.task_model = None  # 针对单任务的情况

        self.task_function: Callable | None = self.function_main
        self.task_available: Callable | None = self.function_available

        self.task_on_activate: Callable | None = self.function_on_activate
        self.task_on_deactivate: Callable | None = self.function_on_deactivate
        self.task_on_enter: Callable | None = self.function_on_enter
        self.task_on_exit: Callable | None = self.function_on_exit

        self.bypass_at_first_run: bool = False  # 是否在第一次运行时跳过 task_on_tick 的执行

        # register to fsm_manager
        if register:
            self.register(fsm_manager=fsm_manager)

        # add task to fsm_manager
        if add_task:
            self.add_task(task_type=task_type)

    def register(
            self,
            fsm_manager: FSMManager
    ) -> FunctionResult:
        """
        Bind the fsm_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = None
        self.task_key = TaskMenuRobotBase.TASK_IDLE

        return FunctionResult.SUCCESS

    def add_task(
            self,
            task_type: TaskFunctionType,
    ) -> FunctionResult:
        """
        Add task to the task manager.
        """

        # add task
        self.fsm_manager.add_task(
            task_name=self.get_key(),
            task_model=self.get_model(),
            task_component=self.get_component(),
            task_update_model=self.get_update_model(),
            task_on_tick=self.get_on_tick(task_type),
            task_available=self.get_available(),
            task_on_activate=self.get_on_activate(),
            task_on_deactivate=self.get_on_deactivate(),
            task_on_enter=self.get_on_enter(),
            task_on_exit=self.get_on_exit(),
        )

        return FunctionResult.SUCCESS

    def get_key(self) -> Enum:
        """
        Return the task key.
        """
        return self.task_key

    def get_name(self) -> str:
        """
        Return the task name.
        """
        return self.task_key.name

    # =====================================================================================================

    def get_model(self) -> Any:
        """
        Return the task_model.
        """
        return self.task_model

    def update_model(
            self,
            model=None,
            stage: Enum | None = None,
            **kwargs,
    ) -> FunctionResult:
        """
        设置任务的模型实例的状态
        """
        if model is not None:
            self.task_model = model

        if self.task_model is None:
            return FunctionResult.SUCCESS

        if stage is not None:
            self.task_model.set_stage(stage)

        return FunctionResult.SUCCESS

    def get_update_model(self) -> Callable | None:
        """
        Get the update_model function of the task.

        任务模型更新函数。
        """

        _function = lambda model=None, stage=None, **kwargs: FunctionResult.SUCCESS

        _function = self.update_model

        self.task_update_model = _function

        return self.task_update_model

    # =====================================================================================================

    def function_available(self, **kwargs) -> bool:
        """
        The available function of the task.
        This function will be called to check if the task is available.
        """
        return True

    # =====================================================================================================

    def function_on_activate(self, **kwargs) -> FunctionResult:
        """
        The on_activate function of the task.
        This function will be called when the task starts.
        """
        return FunctionResult.SUCCESS

    def function_on_deactivate(self, **kwargs) -> FunctionResult:
        """
        The on_deactivate function of the task.
        This function will be called when the task stops.
        """
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def function_on_enter(self, **kwargs) -> FunctionResult:
        """
        The on_enter function of the task.
        This function will be called when the task enters.
        """
        return FunctionResult.SUCCESS

    def function_on_exit(self, **kwargs) -> FunctionResult:
        """
        The on_exit function of the task.
        This function will be called when the task exits.
        """
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def function_main(self, **kwargs) -> FunctionResult:
        """
        The standalone function of the task.
        """
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def get_state(self) -> dict:
        """
        Get the state of the task.
        """
        return {}

    def set_control(self, control: dict) -> FunctionResult:
        """
        Set control parameters of the task.
        """
        return FunctionResult.SUCCESS
