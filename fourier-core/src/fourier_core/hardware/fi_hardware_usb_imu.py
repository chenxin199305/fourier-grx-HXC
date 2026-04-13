from .fi_hardware_logger import Logger
from .fi_hardware_predefine import FunctionResult


def usb_imu_init(self, usb):
    Logger().print_info(f"USB_IMU init: {usb}...")
    return FunctionResult.SUCCESS


def usb_imu_comm(self, usb):
    return FunctionResult.SUCCESS


def usb_imu_check(self, usb):
    return FunctionResult.SUCCESS


def usb_imu_get_quat(self, usb):
    return [0, 0, 0, 1]


def usb_imu_get_angle(self, usb):
    return [0, 0, 0]


def usb_imu_get_acceleration(self, usb):
    return [0, 0, 0]


def usb_imu_get_angular_velocity(self, usb):
    return [0, 0, 0]


def usb_imu_get_magnetometer(self, usb):
    return [0, 0, 0]
