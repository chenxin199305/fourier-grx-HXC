import inspect

from .fi_hardware_predefine import FunctionResult
from .fi_hardware_logger import Logger
from .fi_hardware_base import HardwareBase


class HardwareConnect(HardwareBase):
    def __init__(self):
        super().__init__()

        self.__attr_loaded = False

        self.__fi_ace_functions_loaded = False

        self.__usb_imu_forsense_loaded = False

    def __getattr__(self, item):
        # Lazy load attributes if not already loaded
        self._load_attr()

        return self._get_attr(item)

    # -------------------------------------------------------------------------

    def _load_attr(self) -> FunctionResult:
        if not self.__attr_loaded:
            print(
                f"HardwareConnect.__load_attr: self={self}"
            )
            self.__attr_loaded = True

        super()._load_attr()

        if not self.__fi_ace_functions_loaded:
            self.__load_fi_ace_functions()

        if not self.__usb_imu_forsense_loaded:
            self.__load_usb_imu_forsense_functions()

        return FunctionResult.SUCCESS

    def _get_attr(self, item):
        super_attr = super()._get_attr(item=item)

        # 检查是否是 lambda 函数
        if inspect.isfunction(super_attr) and super_attr.__name__ == "<lambda>":
            pass
        else:
            return super_attr

        fi_ace_functions = {
            "fi_ace_init",
            "fi_ace_comm",
            "fi_ace_check",
            "fi_ace_subscribe",
            ################################
            "fi_ace_set_servo_on",
            "fi_ace_set_servo_off",
            "fi_ace_set_control_mode",
            "fi_ace_set_pd_control",
            "fi_ace_set_pd_param",
            "fi_ace_set_velocity_control",
            "fi_ace_set_velocity_param",
            "fi_ace_get_pvc",
            "fi_ace_get_pvct",
            "fi_ace_get_error",
        }

        if item in fi_ace_functions:
            if hasattr(self, item):
                return getattr(self, item)

        usb_imu_forsense_functions = {
            "usb_imu_forsense_init",
            "usb_imu_forsense_comm",
            "usb_imu_forsense_check",
            ################################
            "usb_imu_forsense_upload",
            "usb_imu_forsense_get_quat",
            "usb_imu_forsense_get_angle",
            "usb_imu_forsense_get_acceleration",
            "usb_imu_forsense_get_angular_velocity",
        }

        if item in usb_imu_forsense_functions:
            if hasattr(self, item):
                return getattr(self, item)

        # Fall back to NOT_IMPLEMENTED for unknown methods
        return lambda *args, **kwargs: FunctionResult.NOT_IMPLEMENTED

    # -------------------------------------------------------------------------

    def __load_fi_ace_functions(self):
        from .fi_hardware_fi_ace import (
            fi_ace_init,
            fi_ace_comm,
            fi_ace_check,
            fi_ace_subscribe,
            fi_ace_set_servo_on,
            fi_ace_set_servo_off,
            fi_ace_set_control_mode,
            fi_ace_set_pd_control,
            fi_ace_set_pd_param,
            fi_ace_set_velocity_control,
            fi_ace_set_velocity_param,
            fi_ace_get_pvc,
            fi_ace_get_pvct,
            fi_ace_get_error,
        )

        self.fi_ace_init = fi_ace_init
        self.fi_ace_comm = fi_ace_comm
        self.fi_ace_check = fi_ace_check
        self.fi_ace_subscribe = fi_ace_subscribe
        self.fi_ace_set_servo_on = fi_ace_set_servo_on
        self.fi_ace_set_servo_off = fi_ace_set_servo_off
        self.fi_ace_set_control_mode = fi_ace_set_control_mode
        self.fi_ace_set_pd_control = fi_ace_set_pd_control
        self.fi_ace_set_pd_param = fi_ace_set_pd_param
        self.fi_ace_set_velocity_control = fi_ace_set_velocity_control
        self.fi_ace_set_velocity_param = fi_ace_set_velocity_param
        self.fi_ace_get_pvc = fi_ace_get_pvc
        self.fi_ace_get_pvct = fi_ace_get_pvct
        self.fi_ace_get_error = fi_ace_get_error

        self.__fi_ace_functions_loaded = True

    # -------------------------------------------------------------------------

    def __load_usb_imu_forsense_functions(self):

        from .fi_hardware_usb_imu_forsense import (
            usb_imu_forsense_init,
            usb_imu_forsense_comm,
            usb_imu_forsense_check,
            usb_imu_forsense_upload,
            usb_imu_forsense_get_quat,
            usb_imu_forsense_get_angle,
            usb_imu_forsense_get_acceleration,
            usb_imu_forsense_get_angular_velocity,
        )

        self.usb_imu_forsense_init = usb_imu_forsense_init
        self.usb_imu_forsense_comm = usb_imu_forsense_comm
        self.usb_imu_forsense_check = usb_imu_forsense_check
        self.usb_imu_forsense_upload = usb_imu_forsense_upload
        self.usb_imu_forsense_get_quat = usb_imu_forsense_get_quat
        self.usb_imu_forsense_get_angle = usb_imu_forsense_get_angle
        self.usb_imu_forsense_get_acceleration = usb_imu_forsense_get_acceleration
        self.usb_imu_forsense_get_angular_velocity = usb_imu_forsense_get_angular_velocity

        self.__usb_imu_forsense_loaded = True

    # -------------------------------------------------------------------------
