from fourier_core.logger import *

from .value_with_history import ValueWithHistory
from .gamepad_controller import GamePadController
from .gamepad_controller_lubancat import GamePadControllerLubancat
from .fi_peripheral_joystick_type import PeripheralJoystickType


class PeripheralJoystick:
    def __init__(self, joystick_type: PeripheralJoystickType | None = None):
        self.type = joystick_type

        if self.type in {
            PeripheralJoystickType.XBOX,
            PeripheralJoystickType.PS4,
            PeripheralJoystickType.PS5,
            PeripheralJoystickType.GAMESIR,
        }:
            self.gamepad_controller = GamePadController()

            # TODO: do not start the gamepad controller here
            # self.gamepad_controller.start()
        elif self.type in {
            PeripheralJoystickType.LUBANCAT,
        }:
            self.gamepad_controller = GamePadControllerLubancat()
        else:
            self.gamepad_controller = None

        self.hat_left_right = ValueWithHistory(0)
        self.hat_up_down = ValueWithHistory(0)

        self.button_cross = ValueWithHistory(0)
        self.button_circle = ValueWithHistory(0)
        self.button_square = ValueWithHistory(0)
        self.button_triangle = ValueWithHistory(0)

        self.button_l1 = ValueWithHistory(0)
        self.button_l2 = ValueWithHistory(0)
        self.button_r1 = ValueWithHistory(0)
        self.button_r2 = ValueWithHistory(0)

        self.button_share = ValueWithHistory(0)
        self.button_option = ValueWithHistory(0)

        self.button_logo = ValueWithHistory(0)
        self.button_axis_left = ValueWithHistory(0)
        self.button_axis_right = ValueWithHistory(0)

        self.axis_left = ValueWithHistory((0, 0))
        self.axis_right = ValueWithHistory((0, 0))

        self.axis_l2 = ValueWithHistory(0)
        self.axis_r2 = ValueWithHistory(0)

        Logger().print_debug(f"Peripheral joystick initialized: {self}")

    def __del__(self):
        if self.gamepad_controller is not None:
            self.gamepad_controller.stop()

    def enable(self):
        """
        Enable the peripheral.
        """

        if self.gamepad_controller is None:
            self.gamepad_controller = GamePadController()
        else:
            pass

        if not self.gamepad_controller.is_alive():
            self.gamepad_controller.start()

        Logger().print_info(f"Peripheral joystick connected: {self}")

    def disable(self):
        """
        Disable the peripheral.
        """

        if self.gamepad_controller is None:
            return

        if self.gamepad_controller.is_alive():
            self.gamepad_controller.stop()
        else:
            pass

        Logger().print_info(f"Peripheral joystick disconnected: {self}")

    def upload(self):
        """
        Upload the joystick status to the peripheral.
        """

        if self.gamepad_controller is None:
            return

        result = self.gamepad_controller.read()

        if self.type == PeripheralJoystickType.XBOX:
            # up
            self.button_triangle.update(result.get("button_west"))
            # down
            self.button_cross.update(result.get("button_north"))
            # left
            self.button_square.update(result.get("button_south"))
            # right
            self.button_circle.update(result.get("button_east"))
        elif self.type == PeripheralJoystickType.GAMESIR:
            # up
            self.button_triangle.update(result.get("button_west"))
            # down
            self.button_cross.update(result.get("button_south"))
            # left
            self.button_square.update(result.get("button_north"))
            # right
            self.button_circle.update(result.get("button_east"))
        else:
            # up
            self.button_triangle.update(result.get("button_north"))
            # down
            self.button_cross.update(result.get("button_south"))
            # left
            self.button_square.update(result.get("button_west"))
            # right
            self.button_circle.update(result.get("button_east"))

        # l is share (select), r is option (start)
        self.button_share.update(result.get("button_select"))
        self.button_option.update(result.get("button_start"))

        self.button_l1.update(result.get("button_l1"))
        self.button_r1.update(result.get("button_r1"))

        if result.get("trigger_lz") > 200:  # 0-255
            self.button_l2.update(1)
        else:
            self.button_l2.update(0)

        if result.get("trigger_rz") > 200:  # 0-255
            self.button_r2.update(1)
        else:
            self.button_r2.update(0)

        self.button_logo.update(result.get("button_mode"))

        self.button_axis_left.update(result.get("button_axis_left"))
        self.button_axis_right.update(result.get("button_axis_right"))

        # in pygame -1 is left/down, 1 is right/up, whereas in inputs, -1 is up/left, 1 is down/right
        if result.get("pad_button_left") == 1:
            self.hat_left_right.update(-1)
        elif result.get("pad_button_right") == 1:
            self.hat_left_right.update(1)
        else:
            self.hat_left_right.update(0)

        if result.get("pad_button_top") == 1:
            self.hat_up_down.update(1)
        elif result.get("pad_button_bottom") == 1:
            self.hat_up_down.update(-1)
        else:
            self.hat_up_down.update(0)

        self.axis_left.update((result.get("left_stick_x"), result.get("left_stick_y")))
        self.axis_right.update((result.get("right_stick_x"), result.get("right_stick_y")))

        self.axis_l2.update(result.get("trigger_lz"))
        self.axis_r2.update(result.get("trigger_rz"))

    def get_state(self):
        """
        返回手柄状态字典
        """
        state_dict = {
            "hat_left_right": self.hat_left_right(),
            "hat_up_down": self.hat_up_down(),
            "button_cross": self.button_cross(),
            "button_circle": self.button_circle(),
            "button_square": self.button_square(),
            "button_triangle": self.button_triangle(),
            "button_l1": self.button_l1(),
            "button_l2": self.button_l2(),
            "button_r1": self.button_r1(),
            "button_r2": self.button_r2(),
            "button_share": self.button_share(),
            "button_option": self.button_option(),
            "button_logo": self.button_logo(),
            "button_axis_left": self.button_axis_left(),
            "button_axis_right": self.button_axis_right(),
            "axis_left": self.axis_left(),
            "axis_right": self.axis_right(),
            "axis_l2": self.axis_l2(),
            "axis_r2": self.axis_r2(),
        }

        return state_dict
