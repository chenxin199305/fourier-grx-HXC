from functools import partial

from fourier_core.config.fi_config import gl_config

from .fi_hardware_predefine import HardwareType
from .fi_hardware_base import HardwareBase
from .fi_hardware_disconnect import HardwareDisconnect
from .fi_hardware_x64 import HardwareX64
from .fi_hardware_logger import Logger


class HardwareManager:
    _instance = None
    type = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            """
            Jason 2025-06-02
            使用 Python 的委托模式（delegation pattern）。
            这样你可以直接通过 HardwareManager 实例来访问硬件实现的方法和属性，而不需要显式地通过 .impl。
            
            1. 移除了 impl 属性，改为使用 _hardware 作为内部实现（前面加下划线表示是内部属性）
            2. 实现了 __getattr__ 方法，这样任何对 HardwareManager 实例的未知属性或方法的访问都会自动委托给 self._hardware
            
            这种方式提供了更干净的接口，同时保持了原有的功能。用户不需要知道底层是通过委托实现的，他们可以像直接使用硬件实现类一样使用 HardwareManager。
            """
            cls._instance._initialize_hardware()

        return cls._instance

    def _initialize_hardware(self):
        if gl_config.parameters.get("device_connected", True) is True:

            if gl_config.parameters.get("hardware_type", HardwareType.X64.value) == HardwareType.X64.value:
                self.type = HardwareType.X64
                self._hardware = HardwareX64()
                Logger().print_success("HardwareInterface device set HardwareX64: hardware platform init X64")

            else:
                self.type = HardwareType.Base
                self._hardware = HardwareBase()
                Logger().print_error("HardwareInterface device set HardwareBase: unknown hardware type")
        else:
            self.type = HardwareType.Disconnect
            self._hardware = HardwareDisconnect()
            Logger().print_warning("HardwareInterface device set HardwareDisconnect: config to disconnected")

    def __getattr__(self, name):
        """
        Delegate unknown attributes/methods to the underlying hardware implementation
        """

        hardware_attr = getattr(self._hardware, name)

        # 如果 hardware_attr 是可调用对象（如方法），则返回一个新的函数
        if callable(hardware_attr):
            # 如果是可调用对象（如方法），且已经绑定到实例上，则直接返回该方法
            if hasattr(hardware_attr, "__self__"):
                return hardware_attr

            """
            Jason 2025-06-02:
            当 hardware_attr 是一个可调用对象（如方法）时
            partial(hardware_attr, self) 会返回一个新函数，这个新函数在被调用时：
            1. 会自动将 self 作为第一个参数传递给 hardware_attr
            2. 然后接收其他参数
            """
            return partial(hardware_attr, self._hardware)

        # 如果 hardware_attr 不是可调用对象，直接返回它
        return hardware_attr

    def __str__(self):
        """
        Print the hardware manager information
        """
        info = f"HardwareManager:\n"
        info += f"  - Hardware Type: {self.type}\n"
        info += f"  - Hardware Implementation: {self._hardware.__class__.__name__}\n"

        return info
