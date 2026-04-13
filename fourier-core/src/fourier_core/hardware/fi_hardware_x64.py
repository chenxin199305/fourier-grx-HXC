import inspect

from .fi_hardware_predefine import FunctionResult
from .fi_hardware_connect import HardwareConnect


class HardwareX64(HardwareConnect):
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
                f"HardwareX64.__load_attr: self={self}"
            )
            self.__attr_loaded = True

        super()._load_attr()

        return FunctionResult.SUCCESS

    def _get_attr(self, item):
        super_attr = super()._get_attr(item=item)

        # 检查是否是 lambda 函数
        if inspect.isfunction(super_attr) and super_attr.__name__ == "<lambda>":
            pass
        else:
            return super_attr

        return lambda *args, **kwargs: FunctionResult.NOT_IMPLEMENTED

    # -------------------------------------------------------------------------
