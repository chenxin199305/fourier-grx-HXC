import sys

from fourier_core.config.fi_config import gl_config

from .fi_hardware_predefine import FunctionResult
from .fi_hardware_logger import Logger

# =============================================================================

if gl_config.parameters.get("hardware_layer") == "fourier-core":
    if gl_config.parameters.get("fi_ace", {}).get("version", "UNKNOWN") == "v1":
        import fourier_core.hardware.fi.ace.fi_ace_client as fi_ace
    else:
        Logger().print_debug("fi_ace version is not set, [default version] will be imported")

        try:
            import fourier_core.hardware.fi.ace.fi_ace_client as fi_ace
        except Exception as e:
            Logger().print_warning("fi_ace not import success!")

    if gl_config.parameters.get("forsense_imu_usb", {}).get("version", "UNKNOWN") == "v1":
        import fourier_core.hardware.forsense.forsense_imu_usb_async_client as forsense_imu_usb
    else:
        Logger().print_debug("forsense_imu_usb version is not set, [default version] will be imported")

        try:
            import fourier_core.hardware.forsense.forsense_imu_usb_async_client as forsense_imu_usb
        except Exception as e:
            Logger().print_warning("forsense_imu_usb not import success!")

# =============================================================================

else:
    Logger().print_error("config file hardware_layer is not supported, program stopped.")
    sys.exit(FunctionResult.FAIL)
