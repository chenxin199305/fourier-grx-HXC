from typing import List

from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualPanel:
    """
    Virtual panel peripheral.

    This class is a singleton class that represents the virtual panel peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return \
            f"##################################################\n" \
            f"PeripheralVirtualPanel: \n" \
            f"command_param_1={self.command_param_1}, \n" \
            f"command_param_2={self.command_param_2}, \n" \
            f"command_param_3={self.command_param_3}, \n" \
            f"command_param_4={self.command_param_4}, \n" \
            f"command_param_5={self.command_param_5}, \n" \
            f"command_param_6={self.command_param_6}, \n" \
            f"command_param_7={self.command_param_7}, \n" \
            f"command_param_8={self.command_param_8}, \n" \
            f"command_param_9={self.command_param_9}, \n" \
            f"command_switch_1={self.command_switch_1}, \n" \
            f"command_switch_2={self.command_switch_2}, \n" \
            f"command_switch_3={self.command_switch_3}, \n" \
            f"command_switch_4={self.command_switch_4}, \n" \
            f"command_switch_5={self.command_switch_5}, \n" \
            f"command_picker_1={self.command_picker_1}, \n" \
            f"command_picker_2={self.command_picker_2}, \n" \
            f"command_picker_3={self.command_picker_3}, \n" \
            f"command_start={self.command_start}, \n" \
            f"command_stop={self.command_stop}, \n" \
            f"command_pause={self.command_pause}, \n" \
            f"##################################################"

    def _create_components(self):
        self.command_param_1 = ValueWithHistory(0.0)
        self.command_param_2 = ValueWithHistory(0.0)
        self.command_param_3 = ValueWithHistory(0.0)
        self.command_param_4 = ValueWithHistory(0.0)
        self.command_param_5 = ValueWithHistory(0.0)
        self.command_param_6 = ValueWithHistory(0.0)
        self.command_param_7 = ValueWithHistory(0.0)
        self.command_param_8 = ValueWithHistory(0.0)
        self.command_param_9 = ValueWithHistory(0.0)

        self.command_switch_1 = ValueWithHistory(False)
        self.command_switch_2 = ValueWithHistory(False)
        self.command_switch_3 = ValueWithHistory(False)
        self.command_switch_4 = ValueWithHistory(False)
        self.command_switch_5 = ValueWithHistory(False)

        self.command_picker_1 = ValueWithHistory(0.0)
        self.command_picker_2 = ValueWithHistory(0.0)
        self.command_picker_3 = ValueWithHistory(0.0)

        self.command_start = ValueWithHistory(False)
        self.command_stop = ValueWithHistory(False)
        self.command_pause = ValueWithHistory(False)

    def update(
            self,
            command_param_1: float | None = None,
            command_param_2: float | None = None,
            command_param_3: float | None = None,
            command_param_4: float | None = None,
            command_param_5: float | None = None,
            command_param_6: float | None = None,
            command_param_7: float | None = None,
            command_param_8: float | None = None,
            command_param_9: float | None = None,
            command_switch_1: bool | None = None,
            command_switch_2: bool | None = None,
            command_switch_3: bool | None = None,
            command_switch_4: bool | None = None,
            command_switch_5: bool | None = None,
            command_picker_1: int | None = None,
            command_picker_2: int | None = None,
            command_picker_3: int | None = None,
            command_start: bool | None = None,
            command_stop: bool | None = None,
            command_pause: bool | None = None,
            **kwargs
    ):
        """
        Update the panel status to the peripheral.
        """
        if command_param_1 is not None:
            self.command_param_1.update(command_param_1)
        if command_param_2 is not None:
            self.command_param_2.update(command_param_2)
        if command_param_3 is not None:
            self.command_param_3.update(command_param_3)
        if command_param_4 is not None:
            self.command_param_4.update(command_param_4)
        if command_param_5 is not None:
            self.command_param_5.update(command_param_5)
        if command_param_6 is not None:
            self.command_param_6.update(command_param_6)
        if command_param_7 is not None:
            self.command_param_7.update(command_param_7)
        if command_param_8 is not None:
            self.command_param_8.update(command_param_8)
        if command_param_9 is not None:
            self.command_param_9.update(command_param_9)

        if command_switch_1 is not None:
            self.command_switch_1.update(command_switch_1)
        if command_switch_2 is not None:
            self.command_switch_2.update(command_switch_2)
        if command_switch_3 is not None:
            self.command_switch_3.update(command_switch_3)
        if command_switch_4 is not None:
            self.command_switch_4.update(command_switch_4)
        if command_switch_5 is not None:
            self.command_switch_5.update(command_switch_5)

        if command_picker_1 is not None:
            self.command_picker_1.update(command_picker_1)
        if command_picker_2 is not None:
            self.command_picker_2.update(command_picker_2)
        if command_picker_3 is not None:
            self.command_picker_3.update(command_picker_3)

        if command_start is not None:
            self.command_start.update(command_start)
        if command_stop is not None:
            self.command_stop.update(command_stop)
        if command_pause is not None:
            self.command_pause.update(command_pause)
