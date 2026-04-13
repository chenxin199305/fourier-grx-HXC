from enum import Enum
from typing import Any
from collections.abc import Callable

from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task.menu import *

from .fi_task_protocol import (
    TaskProtocol,
)


class TaskBase(TaskProtocol):
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
            register: Whether to register the task to the task_manager. (let task know the task_manager)
            add_task: Whether to add the task to the task_manager. (let task_manager know the task)
        """

        if fsm_manager is None:
            raise ValueError("fsm_manager is None")

        self.fsm_manager: FSMManager | None = None
        self.task_type: TaskFunctionType | None = None
        self.task_key: Enum | None = None
        self.task_model = None  # 针对单任务的情况

        self.task_component = None  # 针对多任务的情况

        self.task_available: Callable | None = None

        self.task_on_activate: Callable | None = None
        self.task_on_deactivate: Callable | None = None
        self.task_on_enter: Callable | None = None
        self.task_on_exit: Callable | None = None
        self.task_on_tick: Callable | None = None

        self.bypass_at_first_run: bool = False  # 是否在第一次运行时跳过 task_on_tick 的执行

        # register to fsm_manager
        if register:
            self.register(fsm_manager=fsm_manager)

        # add task to task_manager
        if add_task:
            self.add_task(task_type=task_type)

    def register(
            self,
            fsm_manager: FSMManager
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
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

        self.task_type = task_type

        # add task
        self.fsm_manager.add_task(
            task_name=self.get_key(),
            task_model=self.get_model(),
            task_component=self.get_component(),
            task_update_model=self.get_update_model(),
            task_available=self.get_available(),
            task_on_activate=self.get_on_activate(),
            task_on_deactivate=self.get_on_deactivate(),
            task_on_enter=self.get_on_enter(),
            task_on_exit=self.get_on_exit(),
            task_on_tick=self.get_on_tick(task_type),
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
            model: Any | None = None,
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

    def get_available(self) -> Callable | None:
        """
        Get the available function of the task.

        任务是否可用判定回调函数。
        """

        _function = lambda: True

        _function = self.function_available

        self.task_available = _function

        return self.task_available

    def function_available(self, **kwargs) -> bool:
        """
        The available function of the task.
        This function will be called to check if the task is available.
        """
        return True

    # =====================================================================================================

    def get_on_activate(self) -> Callable | None:
        """
        Get the on_activate function of the task.

        任务被激活时调用的函数。
        """

        _function = lambda: FunctionResult.SUCCESS

        _function = self.function_on_activate

        self.task_on_activate = _function

        return self.task_on_activate

    def get_on_deactivate(self) -> Callable | None:
        """
        Get the on_deactivate function of the task.

        任务被停用时调用的函数。
        """

        _function = lambda: FunctionResult.SUCCESS

        _function = self.function_on_deactivate

        self.task_on_deactivate = _function

        return self.task_on_deactivate

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

    def get_on_enter(self) -> Callable | None:
        """
        Get the on_enter function of the task.

        任务进入时调用的函数。
        """
        _function = lambda: FunctionResult.SUCCESS

        _function = self.function_on_enter

        self.task_on_enter = _function

        return self.task_on_enter

    def get_on_exit(self) -> Callable | None:
        """
        Get the on_exit function of the task.

        任务退出时调用的函数。
        """
        _function = lambda: FunctionResult.SUCCESS

        _function = self.function_on_exit

        self.task_on_exit = _function

        return self.task_on_exit

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

    def get_on_tick(
            self,
            task_type: TaskFunctionType,
    ) -> Callable | None:
        """
        Return the task_on_tick.
        """

        _function = lambda: FunctionResult.SUCCESS

        if task_type == TaskFunctionType.META:
            _function = self._function_meta
        elif task_type == TaskFunctionType.COMPONENT:
            _function = self.function_component
        elif task_type == TaskFunctionType.STANDALONE:
            _function = self.function_standalone
        else:
            raise ValueError(f"Unknown type: {type}")

        def task_function(**kwargs) -> FunctionResult:
            if self.bypass_at_first_run:
                self.bypass_at_first_run = False
                return FunctionResult.SUCCESS

            return _function(**kwargs)

        """
        As get_function will only be called when the task is added to the task manager,
        which means it will only be called once.
        So we can bind the task_on_tick to self.task_on_tick here will not cause any problem.
        """
        self.task_on_tick = task_function

        return self.task_on_tick

    def _function_meta(self, **kwargs) -> FunctionResult:
        """
        The meta function of the task.

        作为任务的元函数，用于任务的核心逻辑处理。
        (在 _function_meta 之外，不再修改 task 本身具有的变量属性，只使用)
        """
        return FunctionResult.SUCCESS

    def function_component(self, **kwargs) -> FunctionResult:
        """
        The component function of the task.

        作为组件任务，只控制使用任务对应关节，不允许操作其他非关联关节，一般是组合使用。
        """
        return FunctionResult.SUCCESS

    def function_standalone(self, **kwargs) -> FunctionResult:
        """
        The standalone function of the task.

        作为独立任务，控制过程会使用所有关节，允许任务独立运行。
        """
        return FunctionResult.SUCCESS

    # =====================================================================================================

    def get_component(self) -> Any:
        """
        Return the task_component.
        """
        return self.task_component

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
