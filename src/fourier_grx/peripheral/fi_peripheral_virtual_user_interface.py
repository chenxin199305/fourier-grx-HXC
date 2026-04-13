from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *

from .fi_peripheral_virtual_user import PeripheralVirtualUser

peripheral_virtual_user: PeripheralVirtualUser | None = None

if gl_config.parameters.get("peripheral", {}).get("use_virtual_user", False):

    try:
        peripheral_virtual_user = PeripheralVirtualUser()

        Logger().print_success(f"Peripheral virtual user connected")

    except ValueError:
        Logger().print_error(f"Peripheral virtual user connect error")
