from enum import Enum
from collections.abc import Callable

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine.fi_task_type import TaskType


class FSMItem:
    def __init__(
            self,
            name: Enum,
            model=None,
            component=None,
            update_model: Callable | None = None,
            available: Callable | None = None,
            on_activate: Callable | None = None,
            on_deactivate: Callable | None = None,
            on_enter: Callable | None = None,
            on_exit: Callable | None = None,
            on_tick: Callable | None = None,
            type: Enum = TaskType.NORMAL,
            **kwargs,
    ):
        """
        任务

        FSMItem Manager 管理的基本单元
        """

        self.name = name.name
        self.value = name.value
        self.model = model
        self.component = component

        if callable(update_model):
            self.update_model = update_model
        else:
            self.update_model = None
            Logger().print_warning(
                f"FSMItem: {self.name}, update_model is not callable. "
                f"(update_model: {update_model})"
            )

        if callable(available):
            self.available = available
        else:
            self.available = lambda: True

        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.on_enter = on_enter
        self.on_exit = on_exit

        if callable(on_tick):
            self.on_tick = on_tick
        else:
            self.on_tick = None
            Logger().print_warning(
                f"FSMItem: {self.name}, on_tick is not callable. "
                f"(on_tick: {on_tick})"
            )

        self.type = type.name

        # 记录任务的状态的变量
        self.on_activate_called = FlagState.CLEAR
        self.on_deactivate_called = FlagState.CLEAR
        self.is_running = FlagState.CLEAR

    def __str__(self):
        return (
            f"FSMItem: \n"
            f"[\n "
            f"name: {self.name}\n "
            f"value: {self.value}\n "
            f"model: {self.model}\n "
            f"component: {self.component}\n "
            f"update_model: {self.update_model}\n "
            f"available: {self.available}\n "
            f"on_activate: {self.on_activate}\n "
            f"on_deactivate: {self.on_deactivate}\n "
            f"on_enter: {self.on_enter}\n "
            f"on_exit: {self.on_exit}\n "
            f"on_tick: {self.on_tick}\n "
            f"type: {self.type}"
            f"]"
        )
