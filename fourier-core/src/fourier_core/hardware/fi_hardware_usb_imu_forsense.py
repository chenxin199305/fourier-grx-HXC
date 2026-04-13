from .fi_hardware_logger import Logger
from .fi_hardware_predefine import FunctionResult
from .fi_hardware_import import forsense_imu_usb


def usb_imu_forsense_init(self, usb):
    Logger().print_info(f"FORSENSE USB_IMU init: "
                        f"usb={usb}...")
    return forsense_imu_usb.init(usb_imu=usb)


def usb_imu_forsense_comm(self, usb, enable=True):
    Logger().print_info(f"FORSENSE USB_IMU comm: "
                        f"usb={usb}, "
                        f"enable={enable}")
    return forsense_imu_usb.comm(usb_imu=usb, enable=enable)


def usb_imu_forsense_check(self, usb):
    return FunctionResult.SUCCESS


def usb_imu_forsense_upload(self, usb):
    return forsense_imu_usb.upload(usb_imu=usb)


def usb_imu_forsense_get_quat(self, usb):
    return forsense_imu_usb.get_quat(usb_imu=usb)


def usb_imu_forsense_get_angle(self, usb):
    return forsense_imu_usb.get_angle(usb_imu=usb)


def usb_imu_forsense_get_acceleration(self, usb):
    return forsense_imu_usb.get_acceleration(usb_imu=usb)


def usb_imu_forsense_get_angular_velocity(self, usb):
    return forsense_imu_usb.get_angular_velocity(usb_imu=usb)
