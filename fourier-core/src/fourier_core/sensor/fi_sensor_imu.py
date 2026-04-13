from fourier_core.predefine import *
from fourier_core.hardware import *

from .fi_sensor_base import SensorBase


# IMU: inertia momentum unit
class SensorIMU(SensorBase):
    def __init__(
            self,
            id="imu",
            config_key="sensor_imu",
    ):
        super().__init__(id=id, config_key=config_key)

        self.measured_quat = [0, 0, 0, 1]
        self.measured_angle = [0, 0, 0]
        self.measured_acceleration = [0, 0, 0]
        self.measured_angular_velocity = [0, 0, 0]
        self.measured_magnetometer = [0, 0, 0]

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
