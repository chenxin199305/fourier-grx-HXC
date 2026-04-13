import numpy
from enum import Enum

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.hardware import *

from .fi_sensor_usb_imu import SensorUSBIMU


# IMU: inertia momentum unit
class SensorUSBIMUForsense(SensorUSBIMU):
    class MODE(Enum):
        DEGREES = "degrees"
        RADIANS = "radians"

    def __init__(
            self,
            usb="/dev/ttyUSB0",
            mode: MODE = MODE.DEGREES,
    ):
        super(SensorUSBIMUForsense, self).__init__(usb=usb)

        self.usb = usb
        self.mode = mode

    def init(self, **kwargs) -> FunctionResult:
        HardwareManager().usb_imu_forsense_init(usb=self.usb)
        return FunctionResult.SUCCESS

    def comm(self, **kwargs) -> FunctionResult:
        self.comm_enable = kwargs.get("enable", True)
        HardwareManager().usb_imu_forsense_comm(usb=self.usb, enable=self.comm_enable)
        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def subscribe(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def upload(self, **kwargs):
        HardwareManager().usb_imu_forsense_upload(usb=self.usb)

        # 默认值
        measured_quat = [0, 0, 0, 1]
        measured_angle = [0, 0, 0]
        measured_angular_velocity = [0, 0, 0]
        measured_acceleration = [0, 0, 0]

        """
        Jason 2025-07-10:
        Forsense IMU sensor data are default to use degrees for angle and angular velocity,
        """
        result_quat = HardwareManager().usb_imu_forsense_get_quat(usb=self.usb)
        result_angle = HardwareManager().usb_imu_forsense_get_angle(usb=self.usb)  # unit : deg
        result_angular_velocity = HardwareManager().usb_imu_forsense_get_angular_velocity(usb=self.usb)  # unit : deg/s
        result_acceleration = HardwareManager().usb_imu_forsense_get_acceleration(usb=self.usb)  # unit : m/s^2

        # print(
        #     f"{self.__class__.__name__} upload() get data: \n"
        #     f"result_quat = {result_quat}\n"
        #     f"result_angle = {result_angle}\n"
        #     f"result_angular_velocity = {result_angular_velocity}\n"
        #     f"result_acceleration = {result_acceleration}\n"
        # )

        # 判断执行函数返回值是否符合类型
        if isinstance(result_quat, list):
            measured_quat = result_quat
        elif isinstance(result_quat, FunctionResult) and result_quat == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("SensorUSBIMUForsense upload() get quat error!!!")
            return FunctionResult.FAIL

        if isinstance(result_angle, list):
            measured_angle = result_angle
        elif isinstance(result_angle, FunctionResult) and result_angle == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("SensorUSBIMUForsense upload() get angle error!!!")
            return FunctionResult.FAIL

        if isinstance(result_angular_velocity, list):
            measured_angular_velocity = result_angular_velocity
        elif isinstance(result_angular_velocity, FunctionResult) and result_angular_velocity == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("SensorUSBIMUForsense upload() get angular velocity error!!!")
            return FunctionResult.FAIL

        if isinstance(result_acceleration, list):
            measured_acceleration = result_acceleration
        elif isinstance(result_acceleration, FunctionResult) and result_acceleration == FunctionResult.SUCCESS:
            pass
        else:
            Logger().print_warning("SensorUSBIMUForsense upload() get acceleration error!!!")
            return FunctionResult.FAIL

        # 数据预处理
        if self.mode == self.MODE.DEGREES:
            # 保持角度不变
            pass
        elif self.mode == self.MODE.RADIANS:
            # 将角度转换为弧度
            measured_angle = [angle * (numpy.pi / 180) for angle in measured_angle]
            measured_angular_velocity = [av * (numpy.pi / 180) for av in measured_angular_velocity]
        else:
            pass

        # 数据更新
        self.measured_quat = measured_quat
        self.measured_angle = measured_angle
        self.measured_angular_velocity = measured_angular_velocity
        self.measured_acceleration = measured_acceleration

        return FunctionResult.SUCCESS
