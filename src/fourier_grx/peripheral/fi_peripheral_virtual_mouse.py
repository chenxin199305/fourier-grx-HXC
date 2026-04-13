from typing import List

from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualMouse:
    """
    Virtual mouse peripheral.

    This class is a singleton class that represents the virtual mouse peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return \
            f"##################################################\n" \
            f"PeripheralVirtualMouse: \n" \
            f"button_left={self.button_left}, \n" \
            f"button_right={self.button_right}, \n" \
            f"button_middle={self.button_middle}, \n" \
            f"axis={self.axis}, \n" \
            f"##################################################"

    def _create_components(self):
        self.button_left = ValueWithHistory(0)
        self.button_right = ValueWithHistory(0)
        self.button_middle = ValueWithHistory(0)

        self.axis = ValueWithHistory((0, 0))

    def update(
            self,
            button_left: int | None = None,
            button_right: int | None = None,
            button_middle: int | None = None,
            axis: List[float] | None = None,
            **kwargs
    ):
        """
        Update the mouse status to the peripheral.
        """
        if button_left is not None:
            self.button_left.update(button_left)
        if button_right is not None:
            self.button_right.update(button_right)
        if button_middle is not None:
            self.button_middle.update(button_middle)

        if axis is not None:
            self.axis.update(axis)
