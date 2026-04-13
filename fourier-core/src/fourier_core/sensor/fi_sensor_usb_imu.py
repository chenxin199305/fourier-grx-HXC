from fourier_core.predefine import *
from fourier_core.hardware import *

from .fi_sensor_imu import SensorIMU


# IMU: inertia momentum unit
class SensorUSBIMU(SensorIMU):
    def __init__(
            self,
            usb="USB1",
            config_key="sensor_usb_imu",
            comm_enable=False,
            comm_frequency=500,  # Default communication frequency in 500Hz
            **kwargs
    ):
        super().__init__(id=usb, config_key=config_key)

        self.usb = usb
        self.comm_enable = comm_enable
        self.comm_frequency = comm_frequency

    def init(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def comm(self, enable=True, frequency=500, **kwargs) -> FunctionResult:
        self.comm_enable = enable
        self.comm_frequency = frequency
        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def subscribe(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def get_measured_quat(self):
        return self.measured_quat

    def get_measured_angle(self):
        return self.measured_angle

    def get_measured_acceleration(self):
        return self.measured_acceleration

    def get_measured_angular_velocity(self):
        return self.measured_angular_velocity

    def get_measured_magnetometer(self):
        return self.measured_magnetometer

    def upload(self, **kwargs):
        self._upload_request()
        return FunctionResult.SUCCESS

    def _upload_request(self):
        return FunctionResult.SUCCESS

    def _upload_measured_quat(self):
        return FunctionResult.SUCCESS

    def _upload_measured_angle(self):
        return FunctionResult.SUCCESS

    def _upload_measured_acceleration(self):
        return FunctionResult.SUCCESS

    def _upload_measured_angular_velocity(self):
        return FunctionResult.SUCCESS

    def _upload_measured_magnetometer(self):
        return FunctionResult.SUCCESS
