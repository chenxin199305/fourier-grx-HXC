from typing import List

from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualKeyboard:
    """
    Virtual keyboard peripheral.

    This class is a singleton class that represents the virtual keyboard peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return \
            f"##################################################\n" \
            f"PeripheralVirtualKeyboard: \n" \
            f"key_up={self.key_up}, \n" \
            f"key_down={self.key_down}, \n" \
            f"key_left={self.key_left}, \n" \
            f"key_right={self.key_right}, \n" \
            f"key_esc={self.key_esc}, \n" \
            f"key_enter={self.key_enter}, \n" \
            f"key_f1={self.key_f1}, \n" \
            f"key_f2={self.key_f2}, \n" \
            f"key_f3={self.key_f3}, \n" \
            f"key_f4={self.key_f4}, \n" \
            f"key_q={self.key_q}, \n" \
            f"key_w={self.key_w}, \n" \
            f"key_e={self.key_e}, \n" \
            f"##################################################"

    def _create_components(self):
        self.key_up = ValueWithHistory(0)
        self.key_down = ValueWithHistory(0)
        self.key_left = ValueWithHistory(0)
        self.key_right = ValueWithHistory(0)

        self.key_esc = ValueWithHistory(0)
        self.key_enter = ValueWithHistory(0)

        self.key_f1 = ValueWithHistory(0)
        self.key_f2 = ValueWithHistory(0)
        self.key_f3 = ValueWithHistory(0)
        self.key_f4 = ValueWithHistory(0)

        self.key_q = ValueWithHistory(0)
        self.key_w = ValueWithHistory(0)
        self.key_e = ValueWithHistory(0)
        self.key_a = ValueWithHistory(0)
        self.key_s = ValueWithHistory(0)
        self.key_d = ValueWithHistory(0)

    def update(
            self,
            key_up: int | None = None,
            key_down: int | None = None,
            key_left: int | None = None,
            key_right: int | None = None,
            key_esc: int | None = None,
            key_enter: int | None = None,
            key_f1: int | None = None,
            key_f2: int | None = None,
            key_f3: int | None = None,
            key_f4: int | None = None,
            key_q: int | None = None,
            key_w: int | None = None,
            key_e: int | None = None,
            key_a: int | None = None,
            key_s: int | None = None,
            key_d: int | None = None,
            **kwargs
    ):
        """
        Update the keyboard status to the peripheral.
        """
        if key_up is not None:
            self.key_up.update(key_up)
        if key_down is not None:
            self.key_down.update(key_down)
        if key_left is not None:
            self.key_left.update(key_left)
        if key_right is not None:
            self.key_right.update(key_right)

        if key_esc is not None:
            self.key_esc.update(key_esc)
        if key_enter is not None:
            self.key_enter.update(key_enter)

        if key_f1 is not None:
            self.key_f1.update(key_f1)
        if key_f2 is not None:
            self.key_f2.update(key_f2)
        if key_f3 is not None:
            self.key_f3.update(key_f3)
        if key_f4 is not None:
            self.key_f4.update(key_f4)

        if key_q is not None:
            self.key_q.update(key_q)
        if key_w is not None:
            self.key_w.update(key_w)
        if key_e is not None:
            self.key_e.update(key_e)
        if key_a is not None:
            self.key_a.update(key_a)
        if key_s is not None:
            self.key_s.update(key_s)
        if key_d is not None:
            self.key_d.update(key_d)
