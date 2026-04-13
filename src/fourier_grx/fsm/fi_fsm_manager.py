import time
from collections import OrderedDict
from collections.abc import Callable
from enum import Enum
from typing import Optional

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm.fi_fsm_item import FSMItem
from fourier_grx.fsm.fi_fsm_data import FSMData


# TODO: use FSMManager to replace the similar function in fourier-core RobotBase
class FSMManager:
    """
    FSMItem Manager is used to manage the tasks in the robot system.
    """

    def __init__(
            self,
            flag_use_joystick: FlagState = FlagState.SET,
            flag_use_keyboard: FlagState = FlagState.SET,
            control_period: Optional[float] = None,
    ):
        # 控制周期
        self.control_period = control_period or 0  # unit: s

        # 任务层级
        self._init_task_management()

        # 组件层级
        self._init_component_management()

        # 任务切换控制源
        self._init_task_selector_joystick(
            flag_use_joystick=flag_use_joystick,
        )
        self._init_task_selector_keyboard(
            flag_use_keyboard=flag_use_keyboard,
        )

    def __str__(self):
        return "FSMManager"

    # --------------------------------------------------

    def _init_task_management(self):
        self.tasks: OrderedDict = OrderedDict()

        self.flag_task_command_update = FlagState.CLEAR
        self.flag_task_running = FlagState.CLEAR

        self.task_select = None
        self.task_select_index = 0  # 用于任务选择索引
        self.task_select_name = ""
        self.task_select_direction = 1  # 用于任务选择方向

        self.task_command = None  # 指令任务编号
        self.task_execute = None  # 执行任务编号
        self.task_executed = None  # 已执行任务编号 （记录上一次执行的任务）
        self.task_data = FSMData()  # 任务数据

        self.task_shortcuts = {
            # 手柄快捷键
            "logo": None,
            "triangle": None,
            "circle": None,
            "square": None,
            "cross": None,

            # 键盘快捷键
            "esc": None,
            "F1": None,
            "F2": None,
            "F3": None,
            "F4": None,
        }

        self.callback_task_select_update = self._callback_task_select_update  # 任务选择更新回调函数
        self.callback_task_command_update = self._callback_task_command_update  # 任务指令更新回调函数

    def _init_component_management(self):
        self.components: OrderedDict = OrderedDict()

        self.flag_component_command_update = FlagState.CLEAR
        self.flag_component_in_process = FlagState.CLEAR

        self.component_select = None
        self.component_select_index = 0  # 用于子任务选择索引
        self.component_select_name = ""
        self.component_select_direction = 1  # 用于子任务选择方向

        self.component_command = None
        self.component_execute = None

        self.callback_component_select_update = self._callback_component_select_update  # 子任务选择更新回调函数
        self.callback_component_command_update = self._callback_component_command_update  # 子任务指令更新回调函数

    def _init_task_selector_joystick(self, flag_use_joystick: FlagState = FlagState.CLEAR):
        """
        Initialize the task selector joystick.
        """
        self.flag_use_joystick = flag_use_joystick

        # 双击切换任务相关变量
        self.double_click_threshold = 0.3  # 双击阈值，单位为秒
        self.last_l2_press_time = 0.0  # 上次按下 L2 键的时间
        self.last_r2_press_time = 0.0  # 上次按下 R2 键的时间
        self.l2_press_count = 0  # L2 键按下计数
        self.r2_press_count = 0  # R2 键按下计数

        # 双击快捷键切换任务相关变量
        self.shortcuts_button_double_click_threshold = 0.3  # 双击阈值，单位为秒
        self.shortcuts_button_last_press_time = {}
        self.shortcuts_button_press_count = {}

    def _init_task_selector_keyboard(self, flag_use_keyboard: FlagState = FlagState.CLEAR):
        """
        Initialize the task selector keyboard.
        """
        self.flag_use_keyboard = flag_use_keyboard

    # =====================================================================================================

    def _callback_task_select_update(self):
        # print the selected task
        if self.task_select is not None:
            Logger().print_info(f"\033[1;37mtask\033[0m select: "
                                f"{self.task_select} "
                                f"(0x{format(self.task_select, '08X')}), "
                                f"name: {self.task_select.name}")
        else:
            Logger().print_info(f"\033[1;37mtask\033[0m select: None")

    def _callback_task_command_update(self):
        # print the selected task
        if self.task_command is not None:
            Logger().print_info(f"\033[1;37mtask\033[0m command: "
                                f"{self.task_command} "
                                f"(0x{format(self.task_command, '08X')}), "
                                f"name: {self.task_command.name}")
        else:
            Logger().print_info(f"\033[1;37mtask\033[0m command: None")

    def _callback_component_select_update(self):
        # print the selected component
        if self.component_select is not None:
            Logger().print_info(f"\033[1;37mcomponent\033[0m select: "
                                f"{self.component_select} "
                                f"(0x{format(self.component_select, '08X')}), "
                                f"name: {self.component_select.name}")
        else:
            Logger().print_info(f"\033[1;37mcomponent\033[0m select: None")

    def _callback_component_command_update(self):
        # print the selected component
        if self.component_command is not None:
            Logger().print_info(f"\033[1;37mcomponent\033[0m command: "
                                f"{self.component_command} "
                                f"(0x{format(self.component_command, '08X')}), "
                                f"name: {self.component_command.name}")
        else:
            Logger().print_info(f"\033[1;37mcomponent\033[0m command: None")

    # =====================================================================================================

    def _update_from_joystick(self) -> None | FunctionResult:
        """
        Update the task from the joystick
        """
        if self.flag_use_joystick == FlagState.CLEAR:
            return None

        # --------------------------------------------

        # imports
        from fourier_grx.peripheral import peripheral_joystick

        if peripheral_joystick is not None:
            # update the joystick state
            peripheral_joystick.upload()
        else:
            return None

        # --------------------------------------------
        # 任务层级

        # task select
        if peripheral_joystick.button_l1.current == 1 != peripheral_joystick.button_l1.last:
            self.task_select_index += self.task_select_direction  # 更新索引

            if len(self.tasks) > 0:
                self.task_select_index %= len(self.tasks)  # 防止索引越界
                self.task_select = list(self.tasks.keys())[self.task_select_index]  # 选中任务
            else:
                self.task_select_index = 0
                self.task_select = None

            # callback
            if callable(self.callback_task_select_update):
                self.callback_task_select_update()

        # task assign
        # if peripheral_joystick.button_l2.current == 1 != peripheral_joystick.button_l2.last:
        #     self.set_task_command(task_command=self.task_select)
        # 检查按钮是否被按下
        if peripheral_joystick.button_l2.current == 1 \
                and peripheral_joystick.button_l2.current != peripheral_joystick.button_l2.last:
            current_time = time.time()

            # 检查时间差
            if current_time - self.last_l2_press_time < self.double_click_threshold:
                self.l2_press_count += 1
            else:
                self.l2_press_count = 1  # 重置计数

            # 更新上次按下时间
            self.last_l2_press_time = current_time

            # 如果是双击，则执行任务
            if self.l2_press_count == 2:
                self.set_task_command(task_command=self.task_select)

                # 重置计数器
                self.l2_press_count = 0

        # task select direction
        if peripheral_joystick.button_share.current == 1 and peripheral_joystick.button_share.last == 0:
            self.task_select_direction = -self.task_select_direction
            Logger().print_info("task select direction: " + str(self.task_select_direction))

        # task shortcuts
        shortcuts_button_mapping = {
            "logo": peripheral_joystick.button_logo,
            "triangle": peripheral_joystick.button_triangle,
            "circle": peripheral_joystick.button_circle,
            "square": peripheral_joystick.button_square,
            "cross": peripheral_joystick.button_cross
        }

        for button_name, button in shortcuts_button_mapping.items():
            # 初始化按钮的计时器和计数器（如果不存在）
            if button_name not in self.shortcuts_button_last_press_time:
                self.shortcuts_button_last_press_time[button_name] = 0.0

            if button_name not in self.shortcuts_button_press_count:
                self.shortcuts_button_press_count[button_name] = 0

            # 检查按钮是否被按下
            if button.current == 1 \
                    and button.current != button.last:
                current_time = time.time()

                # 检查时间差
                if current_time - self.shortcuts_button_last_press_time[button_name] \
                        < self.shortcuts_button_double_click_threshold:
                    self.shortcuts_button_press_count[button_name] += 1
                else:
                    self.shortcuts_button_press_count[button_name] = 1  # 重置计数

                # 更新上次按下时间
                self.shortcuts_button_last_press_time[button_name] = current_time

                # 如果是双击，则执行任务
                if self.shortcuts_button_press_count[button_name] == 2:
                    # 检查是否有对应的快捷任务
                    if self.task_shortcuts.get(button_name):
                        self.set_task_command(task_command=self.task_shortcuts.get(button_name))
                    else:
                        Logger().print_warning(f"No shortcut task is assigned to {button_name}.")

                    # 重置计数器
                    self.shortcuts_button_press_count[button_name] = 0

                # if self.task_shortcuts.get(button_name):
                #     self.set_task_command(task_command=self.task_shortcuts.get(button_name))
                # else:
                #     Logger().print_warning(f"No shortcut task is assigned to {button_name}.")

        # --------------------------------------------
        # 组件层级

        # component select
        if peripheral_joystick.button_r1.current == 1 != peripheral_joystick.button_r1.last:
            self.component_select_index += self.component_select_direction  # 更新索引

            if len(self.components) > 0:
                self.component_select_index %= len(self.components)  # 防止索引越界
                self.component_select = list(self.components.keys())[self.component_select_index]  # 选中组件
            else:
                self.component_select_index = 0  # 防止索引越界
                self.component_select = None

            # callback
            if callable(self.callback_component_select_update):
                self.callback_component_select_update()

        # component assign
        # if peripheral_joystick.button_r2.current == 1 != peripheral_joystick.button_r2.last:
        #     self.set_component_command(self.component_select)
        # 检查按钮是否被按下
        if peripheral_joystick.button_r2.current == 1 \
                and peripheral_joystick.button_r2.current != peripheral_joystick.button_r2.last:
            current_time = time.time()

            # 检查时间差
            if current_time - self.last_r2_press_time < self.double_click_threshold:
                self.r2_press_count += 1
            else:
                self.r2_press_count = 1

            # 更新上次按下时间
            self.last_r2_press_time = current_time

            # 如果是双击，则执行组件
            if self.r2_press_count == 2:
                self.set_component_command(component_command=self.component_select)

                # 重置计数器
                self.r2_press_count = 0

        # component select direction
        if peripheral_joystick.button_option.current == 1 and peripheral_joystick.button_option.last == 0:
            self.component_select_direction = -self.component_select_direction
            Logger().print_info("component select direction: " + str(self.component_select_direction))

        # --------------------------------------------

        return FunctionResult.SUCCESS

    def _update_from_keyboard(self) -> None | FunctionResult:
        """
        Update the task from the keyboard
        """
        if self.flag_use_keyboard == FlagState.CLEAR:
            return None

        # --------------------------------------------

        # imports
        from fourier_grx.peripheral import peripheral_keyboard

        if peripheral_keyboard is not None:
            # update the keyboard state
            peripheral_keyboard.upload()
        else:
            return None

        # --------------------------------------------
        # 任务层级

        # task select
        if peripheral_keyboard.key_down.current == 1 != peripheral_keyboard.key_down.last:
            """
            键盘的按键方向和任务的切换方向是相反的，这样更符合人的习惯
            """
            self.task_select_index += 1

            if len(self.tasks) > 0:
                self.task_select_index %= len(self.tasks)  # 防止索引越界
                self.task_select = list(self.tasks.keys())[self.task_select_index]  # 选中任务
            else:
                self.task_select_index = 0
                self.task_select = None

            # callback
            if callable(self.callback_task_select_update):
                self.callback_task_select_update()

        if peripheral_keyboard.key_up.current == 1 != peripheral_keyboard.key_up.last:
            """
            键盘的按键方向和任务的切换方向是相反的，这样更符合人的习惯
            """
            self.task_select_index -= 1

            if len(self.tasks) > 0:
                self.task_select_index %= len(self.tasks)  # 防止索引越界
                self.task_select = list(self.tasks.keys())[self.task_select_index]  # 选中任务
            else:
                self.task_select_index = 0
                self.task_select = None

            # callback
            if callable(self.callback_task_select_update):
                self.callback_task_select_update()

        # task assign
        if peripheral_keyboard.key_return.current == 1 != peripheral_keyboard.key_return.last:
            self.set_task_command(task_command=self.task_select)

        # task shortcuts
        shortcuts_key_mapping = {
            "esc": peripheral_keyboard.key_esc,
            "F1": peripheral_keyboard.key_f1,
            "F2": peripheral_keyboard.key_f2,
            "F3": peripheral_keyboard.key_f3,
            "F4": peripheral_keyboard.key_f4
        }

        for key_name, key in shortcuts_key_mapping.items():
            if key.current == 1 != key.last:
                if self.task_shortcuts.get(key_name):
                    self.set_task_command(task_command=self.task_shortcuts.get(key_name))
                else:
                    Logger().print_warning(f"No shortcut task is assigned to {key_name}.")

        # --------------------------------------------
        # 组件层级

        # --------------------------------------------

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def check_task_command(self, task_command, value_type="enum") -> FunctionResult:
        """
        检查任务指令的有效性。

        :param task_command: 任务指令，通常是一个枚举类型的任务编号。
        :param value_type: 指定任务指令的类型，默认为 "enum"。 可选 "enum" 或 "value"。
        :return: FunctionResult.SUCCESS 如果任务指令有效，否则返回 FunctionResult.FAIL。
        """

        if value_type == "enum":
            if task_command in self.tasks:
                return FunctionResult.SUCCESS
        elif value_type == "value":
            for key, value in self.tasks.items():
                if key == int(task_command):
                    return FunctionResult.SUCCESS
        else:
            if isinstance(task_command, Enum):
                if task_command in self.tasks:
                    return FunctionResult.SUCCESS
            else:
                raise ValueError(
                    f"{self.__class__.__name__}.check_task_command Invalid value_type. Must be 'enum' or 'value'."
                )

        return FunctionResult.FAIL

    def set_task_command(self, task_command, value_type="enum") -> FunctionResult:
        """
        设置任务指令，更新任务状态。

        :param task_command: 任务指令，通常是一个枚举类型的任务编号。
        :param value_type: 指定任务指令的类型，默认为 "enum"。 可选 "enum" 或 "value"。
        """

        self.flag_task_command_update = FlagState.SET

        if value_type == "enum":
            self.task_command = task_command
        elif value_type == "value":
            self.task_command = task_command
            for key, value in self.tasks.items():
                if key == int(task_command):
                    self.task_command = key
                    break
        else:
            if isinstance(task_command, Enum):
                self.task_command = task_command
            else:
                raise ValueError(
                    f"{self.__class__.__name__}.set_task_command Invalid value_type. Must be 'enum' or 'value'."
                )

        # callback
        if callable(self.callback_task_command_update):
            self.callback_task_command_update()

        return FunctionResult.SUCCESS

    def set_component_command(self, component_command, value_type="enum") -> FunctionResult:
        """
        设置组件指令，更新组件状态。

        :param component_command: 组件指令，通常是一个枚举类型的组件编号。
        :param value_type: 指定组件指令的类型，默认为 "enum"。 可选 "enum" 或 "value"。
        """

        self.flag_component_command_update = FlagState.SET

        if value_type == "enum":
            self.component_command = component_command
        elif value_type == "value":
            for key, value in self.components.items():
                if key == int(component_command):
                    self.component_command = key
                    break
        else:
            if isinstance(component_command, Enum):
                self.component_command = component_command
            else:
                raise ValueError(
                    f"{self.__class__.__name__}.set_component_command Invalid value_type. Must be 'enum' or 'value'."
                )

        # callback
        if callable(self.callback_component_command_update):
            self.callback_component_command_update()

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def update(self, task_command=None) -> FunctionResult:
        # 更新输入源及任务信息
        self._update_from_joystick()
        self._update_from_keyboard()

        # 更新任务信息
        if task_command is not None:
            self.set_task_command(task_command=task_command)

        # 检查任务和组件是否可用
        # 检查任务和组件是否可用
        self._handle_check_task_available()
        self._handle_check_component_available()

        # 处理任务命令更新
        # 处理组件命令更新
        self._handle_task_command_update()
        self._handle_component_command_update()

        return FunctionResult.SUCCESS

    def _handle_check_task_available(self) -> FunctionResult:
        """ 检查任务是否可用，更新任务标志位状态 """

        if self.flag_task_command_update == FlagState.SET:
            command_task = self.tasks.get(self.task_command)

            available = self._execute_task_callback(command_task, "available")

            # 如果任务不可用，则不切换任务
            if available:
                pass
            else:
                # 如果任务不可用，则清除更新标志位
                self.flag_task_command_update = FlagState.CLEAR

                # 打印警告信息
                Logger().print_warning(f"\033[1;37mtask\033[0m command: "
                                       f"{self.task_command} "
                                       f"{self.task_command.name} "
                                       f"is not available at current state. Command update skipped.")

        return FunctionResult.SUCCESS

    def _handle_check_component_available(self) -> FunctionResult:
        """ 检查组件是否可用，更新组件标志位状态 """

        if self.flag_task_command_update == FlagState.SET:
            pass

        return FunctionResult.SUCCESS

    def _handle_task_command_update(self) -> FunctionResult:
        """处理任务命令更新，设置算法模型的状态"""

        # 检查任务更新标志位
        if self.flag_task_command_update == FlagState.SET:
            self.flag_task_command_update = FlagState.CLEAR
        else:
            return FunctionResult.SUCCESS

        # 排除任务指令为空的情况
        if self.task_command is None:
            return FunctionResult.SUCCESS

        # 复位任务模型状态
        self._handle_task_model_stage_update(task=self.tasks[self.task_command])

        # 清除任务组件及其状态
        self.components.clear()
        self.component_select = None  # 清除组件选择任务
        self.component_command = None  # 清除组件指令任务
        self.component_execute = None  # 清除组件执行任务

        # 更新任务组件状态
        task_component = self.tasks[self.task_command].component
        if task_component is not None:
            self._handle_task_component_stage_update(task_component=task_component)

            # 获取全部组件清单，更新 task_manager 的 components 清单
            self._handle_task_component_dict_update(task_component=task_component)
        else:
            # 任务组件为空
            pass

        # 更新任务执行状态
        self.task_execute = self.task_command

        # 重置任务指令
        self.task_command = None

        return FunctionResult.SUCCESS

    def _handle_component_command_update(self) -> FunctionResult:
        """处理组件命令更新，设置组件的状态"""

        # 检查组件更新标志位
        if self.flag_component_command_update == FlagState.SET:
            self.flag_component_command_update = FlagState.CLEAR
        else:
            return FunctionResult.SUCCESS

        # 排除组件指令为空的情况
        if self.component_command is None:
            return FunctionResult.SUCCESS

        # 复位组件模型状态
        task_component = self.components[self.component_command]
        self._handle_task_model_stage_update(task=task_component)

        # 更新组件执行状态
        self.component_execute = self.component_command

        # 重置组件指令
        self.component_command = None

        return FunctionResult.SUCCESS

    def _handle_task_model_stage_update(self, task) -> FunctionResult:
        """处理任务模型更新"""
        if task is not None:
            # 根据任务执行状态设置算法阶段
            target_stage = (AlgorithmStage.STAGE_INIT
                            if self.task_execute != self.task_command
                            else AlgorithmStage.STAGE_START)

            # 更新任务模型状态
            task.update_model(stage=target_stage)

        return FunctionResult.SUCCESS

    def _handle_task_component_stage_update(self, task_component) -> FunctionResult:
        """处理任务组件更新"""
        if task_component is not None:
            if isinstance(task_component, list):
                for component in task_component:
                    # ------------------------------------------------------------
                    # 循环递归处理
                    self._handle_task_model_stage_update(task=component)

                    task_component = component.task_component
                    self._handle_task_component_stage_update(task_component=task_component)
                    # ------------------------------------------------------------
            else:
                raise ValueError("task_component is not a list")

        return FunctionResult.SUCCESS

    def _handle_task_component_dict_update(self, task_component) -> FunctionResult:
        """更新任务组件清单"""
        if task_component is not None:
            if isinstance(task_component, list):
                for component in task_component:
                    # ------------------------------------------------------------
                    # 循环递归处理
                    self.components.update({
                        component.get_key(): component
                    })

                    task_component = component.task_component
                    self._handle_task_component_dict_update(task_component=task_component)
                    # ------------------------------------------------------------
            else:
                raise ValueError("task_component is not a list")

        return FunctionResult.SUCCESS

    # ------------------------------------------------------------

    def execute(self) -> FunctionResult:
        """执行当前任务"""
        if self.task_execute is None:
            return FunctionResult.SUCCESS

        current_task = self.tasks.get(self.task_execute)
        last_task = self.tasks.get(self.task_executed)

        # TODO: 切换任务时，判断是否可以进行切换
        # if self.task_executed != self.task_execute:
        #     available = self._execute_task_callback(current_task, "available")
        #
        #     # 如果任务不可用，则不切换任务
        #     if available:
        #         pass
        #     else:
        #         # TODO: 更新任务 (恢复之前执行的任务)
        #         # self.task_execute = self.task_executed
        #         #
        #         # current_task = self.tasks.get(self.task_execute)
        #         # last_task = self.tasks.get(self.task_executed)
        #         pass

        # 切换任务时，处理旧任务的停止和新任务的启动
        if self.task_executed != self.task_execute:
            self._execute_task_callback(last_task, "on_deactivate")
            self._execute_task_callback(current_task, "on_activate")

        # 执行任务函数
        self._execute_task_callback(current_task, "on_enter")
        self._execute_task_callback(current_task, "on_tick")
        self._execute_task_callback(current_task, "on_exit")

        # 更新任务处理状态标志
        self.flag_task_running = (FlagState.SET
                                  if current_task.type == TaskType.NORMAL
                                  else FlagState.CLEAR)
        # 更新已执行任务编号
        self.task_executed = self.task_execute

        return FunctionResult.SUCCESS

    def _execute_task_callback(self, task, callback_name: str):
        """ 执行任务的回调函数 """
        if task is not None:
            callback = getattr(task, callback_name, None)
            if callable(callback):
                return callback()

        return None

    # =====================================================================================================

    def log_task_info(self) -> FunctionResult:
        Logger().print_info("#################################")
        Logger().print_info("FSMItem info: ")

        # print all tasks
        for task_name, task in self.tasks.items():
            Logger().print_info(f"task key: {task_name}, value: {task.name}")

        return FunctionResult.SUCCESS

    def add_task(
            self,
            task_name: Enum,
            task_model=None,
            task_component=None,
            task_update_model: Callable | None = None,
            task_available: Callable | None = None,
            task_on_activate: Callable | None = None,
            task_on_deactivate: Callable | None = None,
            task_on_enter: Callable | None = None,
            task_on_exit: Callable | None = None,
            task_on_tick: Callable | None = None,
            task_type=TaskType.NORMAL,
    ) -> FunctionResult:
        """
        Jason 2025-06-06:
        这里将 TaskBase (TaskProtocol) 转换成 FSMItem 实例，并添加到任务管理器中。
        """
        # create task
        self.tasks.update({
            task_name: FSMItem(name=task_name,
                               model=task_model,
                               component=task_component,
                               update_model=task_update_model,
                               available=task_available,
                               on_activate=task_on_activate,
                               on_deactivate=task_on_deactivate,
                               on_enter=task_on_enter,
                               on_exit=task_on_exit,
                               on_tick=task_on_tick,
                               type=task_type)
        })

        return FunctionResult.SUCCESS

    def remove_task(
            self,
            task_name: Enum
    ) -> FunctionResult:
        if task_name in self.tasks:
            del self.tasks[task_name]

        return FunctionResult.SUCCESS

    def clear_tasks(self) -> FunctionResult:
        self.tasks.clear()

        return FunctionResult.SUCCESS

    # =====================================================================================================
