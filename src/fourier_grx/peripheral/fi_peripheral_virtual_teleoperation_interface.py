from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_teleoperation import PeripheralVirtualTeleoperation

peripheral_virtual_teleoperation: PeripheralVirtualTeleoperation | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_teleoperation", False):

    try:
        peripheral_virtual_teleoperation = PeripheralVirtualTeleoperation()

        Logger().print_success(f"Peripheral virtual teleoperation connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual teleoperation connect error")
