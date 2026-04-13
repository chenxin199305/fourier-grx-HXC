from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_mouse import PeripheralVirtualMouse

peripheral_virtual_mouse: PeripheralVirtualMouse | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_mouse", False):

    try:
        peripheral_virtual_mouse = PeripheralVirtualMouse()

        Logger().print_success(f"Peripheral virtual mouse connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual mouse connect error")
