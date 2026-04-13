from typing import List

from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualJoystick:
    """
    Virtual joystick peripheral.

    This class is a singleton class that represents the virtual joystick peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return \
            f"##################################################\n" \
            f"PeripheralVirtualJoystick: \n" \
            f"button_up={self.button_up}, \n" \
            f"button_down={self.button_down}, \n" \
            f"button_left={self.button_left}, \n" \
            f"button_right={self.button_right}, \n" \
            f"button_l1={self.button_l1}, \n" \
            f"button_l2={self.button_l2}, \n" \
            f"button_r1={self.button_r1}, \n" \
            f"button_r2={self.button_r2}, \n" \
            f"button_share={self.button_share}, \n" \
            f"button_option={self.button_option}, \n" \
            f"button_logo={self.button_logo}, \n" \
            f"button_axis_left={self.button_axis_left}, \n" \
            f"button_axis_right={self.button_axis_right}, \n" \
            f"axis_left={self.axis_left}, \n" \
            f"axis_right={self.axis_right}, \n" \
            f"axis_l2={self.axis_l2}, \n" \
            f"axis_r2={self.axis_r2}, \n" \
            f"hat_left_right={self.hat_left_right}, \n" \
            f"hat_up_down={self.hat_up_down}, \n" \
            f"##################################################"

    def _create_components(self):
        self.button_up = ValueWithHistory(0)
        self.button_down = ValueWithHistory(0)
        self.button_left = ValueWithHistory(0)
        self.button_right = ValueWithHistory(0)

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

        self.hat_left_right = ValueWithHistory(0)
        self.hat_up_down = ValueWithHistory(0)

    def update(
            self,
            button_up: int | None = None,
            button_down: int | None = None,
            button_left: int | None = None,
            button_right: int | None = None,
            button_l1: int | None = None,
            button_l2: int | None = None,
            button_r1: int | None = None,
            button_r2: int | None = None,
            button_share: int | None = None,
            button_option: int | None = None,
            button_logo: int | None = None,
            button_axis_left: int | None = None,
            button_axis_right: int | None = None,
            axis_left: List[float] | None = None,
            axis_right: List[float] | None = None,
            axis_l2: int | None = None,
            axis_r2: int | None = None,
            hat_left_right: int | None = None,
            hat_up_down: int | None = None,
            **kwargs
    ):
        """
        Update the joystick status to the peripheral.
        """
        if button_up is not None:
            self.button_up.update(button_up)
        if button_down is not None:
            self.button_down.update(button_down)
        if button_left is not None:
            self.button_left.update(button_left)
        if button_right is not None:
            self.button_right.update(button_right)

        if button_share is not None:
            self.button_share.update(button_share)
        if button_option is not None:
            self.button_option.update(button_option)

        if button_l1 is not None:
            self.button_l1.update(button_l1)
        if button_r1 is not None:
            self.button_r1.update(button_r1)
        if button_l2 is not None:
            self.button_l2.update(button_l2)
        if button_r2 is not None:
            self.button_r2.update(button_r2)

        if button_logo is not None:
            self.button_logo.update(button_logo)

        if button_axis_left is not None:
            self.button_axis_left.update(button_axis_left)
        if button_axis_right is not None:
            self.button_axis_right.update(button_axis_right)

        if axis_left is not None:
            self.axis_left.update(axis_left)
        if axis_right is not None:
            self.axis_right.update(axis_right)

        if axis_l2 is not None:
            self.axis_l2.update(axis_l2)
        if axis_r2 is not None:
            self.axis_r2.update(axis_r2)

        if hat_left_right is not None:
            self.hat_left_right.update(hat_left_right)
        if hat_up_down is not None:
            self.hat_up_down.update(hat_up_down)
