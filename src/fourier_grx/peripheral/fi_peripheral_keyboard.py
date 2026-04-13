from fourier_core.logger import *

from .value_with_history import ValueWithHistory
from .keyboard_controller import KeyboardController
from .fi_peripheral_keyboard_type import PeripheralKeyboardType


class PeripheralKeyboard:
    def __init__(self, keyboard_type: PeripheralKeyboardType | None = None):
        self.type = keyboard_type

        if self.type is not None:
            self.keyboard_controller = KeyboardController()

            # TODO: do not start the keyboard controller here
            # self.keyboard_controller.start()
        else:
            self.keyboard_controller = None

        self.key_up = ValueWithHistory(0)
        self.key_down = ValueWithHistory(0)
        self.key_left = ValueWithHistory(0)
        self.key_right = ValueWithHistory(0)

        self.key_return = ValueWithHistory(0)
        self.key_esc = ValueWithHistory(0)
        self.key_space = ValueWithHistory(0)

        self.key_f1 = ValueWithHistory(0)
        self.key_f2 = ValueWithHistory(0)
        self.key_f3 = ValueWithHistory(0)
        self.key_f4 = ValueWithHistory(0)
        self.key_f5 = ValueWithHistory(0)
        self.key_f6 = ValueWithHistory(0)
        self.key_f7 = ValueWithHistory(0)
        self.key_f8 = ValueWithHistory(0)

        self.key_w = ValueWithHistory(0)
        self.key_a = ValueWithHistory(0)
        self.key_s = ValueWithHistory(0)
        self.key_d = ValueWithHistory(0)
        self.key_q = ValueWithHistory(0)
        self.key_e = ValueWithHistory(0)

        Logger().print_debug(f"Peripheral keyboard initialized: {self}")

    def __del__(self):
        if self.keyboard_controller is not None:
            self.keyboard_controller.stop()

    def enable(self):
        """
        Enable the peripheral.
        """

        if self.keyboard_controller is None:
            self.keyboard_controller = KeyboardController()
        else:
            pass

        if not self.keyboard_controller.is_alive():
            self.keyboard_controller.start()

        Logger().print_success(f"Peripheral keyboard connected: {self}")

    def disable(self):
        """
        Disable the peripheral.
        """

        if self.keyboard_controller is None:
            return

        if self.keyboard_controller.is_alive():
            self.keyboard_controller.stop()
        else:
            pass

        Logger().print_info(f"Peripheral keyboard disconnected: {self}")

    def upload(self):
        """
        Upload the keyboard status to the peripheral.
        """

        if self.keyboard_controller is None:
            return

        result = self.keyboard_controller.read()

        self.key_up.update(result.get("KEY_UP"))
        self.key_down.update(result.get("KEY_DOWN"))
        self.key_left.update(result.get("KEY_LEFT"))
        self.key_right.update(result.get("KEY_RIGHT"))

        self.key_return.update(result.get("KEY_ENTER"))
        self.key_esc.update(result.get("KEY_ESC"))
        self.key_space.update(result.get("KEY_SPACE"))

        self.key_f1.update(result.get("KEY_F1"))
        self.key_f2.update(result.get("KEY_F2"))
        self.key_f3.update(result.get("KEY_F3"))
        self.key_f4.update(result.get("KEY_F4"))
        self.key_f5.update(result.get("KEY_F5"))
        self.key_f6.update(result.get("KEY_F6"))
        self.key_f7.update(result.get("KEY_F7"))
        self.key_f8.update(result.get("KEY_F8"))

        self.key_w.update(result.get("KEY_W"))
        self.key_a.update(result.get("KEY_A"))
        self.key_s.update(result.get("KEY_S"))
        self.key_d.update(result.get("KEY_D"))
        self.key_q.update(result.get("KEY_Q"))
        self.key_e.update(result.get("KEY_E"))

    def get_state(self):
        """
        返回键盘当前状态字典。
        """
        return {
            "key_up": self.key_up(),
            "key_down": self.key_down(),
            "key_left": self.key_left(),
            "key_right": self.key_right(),
            "key_return": self.key_return(),
            "key_esc": self.key_esc(),
            "key_space": self.key_space(),
            "key_f1": self.key_f1(),
            "key_f2": self.key_f2(),
            "key_f3": self.key_f3(),
            "key_f4": self.key_f4(),
            "key_f5": self.key_f5(),
            "key_f6": self.key_f6(),
            "key_f7": self.key_f7(),
            "key_f8": self.key_f8(),
            "key_w": self.key_w(),
            "key_a": self.key_a(),
            "key_s": self.key_s(),
            "key_d": self.key_d(),
            "key_q": self.key_q(),
            "key_e": self.key_e(),
        }
