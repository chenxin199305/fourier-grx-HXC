from .fi_hardware_logger import Logger
from .fi_hardware_predefine import FunctionResult
from .fi_hardware_base import HardwareBase


class HardwareDisconnect(HardwareBase):
    def __init__(self):
        super().__init__()

        self.__attr_loaded = False

    def __getattr__(self, item):
        # Lazy load attributes if not already loaded
        self._load_attr()

        return self._get_attr(item)

    # -------------------------------------------------------------------------

    def _load_attr(self) -> FunctionResult:
        if not self.__attr_loaded:
            print(
                f"HardwareDisconnect.__load_attr: self={self}"
            )
            self.__attr_loaded = True

        return FunctionResult.SUCCESS

    def _get_attr(self, item):
        return lambda *args, **kwargs: FunctionResult.SUCCESS

    # -------------------------------------------------------------------------
