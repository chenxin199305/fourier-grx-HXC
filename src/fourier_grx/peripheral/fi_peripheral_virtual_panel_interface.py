from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_panel import PeripheralVirtualPanel

peripheral_virtual_panel: PeripheralVirtualPanel | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_panel", False):

    try:
        peripheral_virtual_panel = PeripheralVirtualPanel()

        Logger().print_success(f"Peripheral virtual panel connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual panel connect error")
