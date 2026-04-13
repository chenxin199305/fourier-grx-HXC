from fourier_core.predefine import *
from fourier_core.sensor.fi_sensor_base import SensorBase


class SensorManager:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.sensors = []
            cls._instance.number_of_sensor_usb_imu = 0
            cls._instance.sensor_usb_imus = []

        return cls._instance

    def __str__(self):
        """
        打印 Manager 和 Sensor 的信息
        """
        info = f"SensorManager:\n"
        for sensor in self.sensors:
            info += f"  - {sensor.id}: {sensor}\n"
        return info

    def add_sensor(self, sensor: SensorBase) -> FunctionResult:
        if not isinstance(sensor, SensorBase):
            raise TypeError("sensor must be an instance of SensorBase")

        self.sensors.append(sensor)

        return FunctionResult.SUCCESS

    def remove_sensor(self, sensor: SensorBase):
        if not isinstance(sensor, SensorBase):
            raise TypeError("sensor must be an instance of SensorBase")

        if sensor in self.sensors:
            self.sensors.remove(sensor)
            return FunctionResult.SUCCESS

        return FunctionResult.FAIL

    def get_number_of_sensors(self, sensor_type=None) -> int:
        """
        获取传感器数量

        :param sensor_type: 传感器类型，必须是 SensorBase 的子类
        """
        # If no specific type is provided, return the total number of sensors
        if sensor_type is None:
            return len(self.sensors)

        # If a specific type is provided, count the sensors of that type
        number_of_sensors = 0

        for sensor in self.sensors:
            if isinstance(sensor, sensor_type):
                number_of_sensors += 1

        return number_of_sensors

    def get_sensor_list(self, sensor_type=None) -> list:
        """
        获取传感器列表

        :param sensor_type: 传感器类型，必须是 SensorBase 的子类
        """
        # If no specific type is provided, return all sensors
        if sensor_type is None:
            return self.sensors

        # If a specific type is provided, filter the sensors by that type
        sensor_list = []

        for sensor in self.sensors:
            if isinstance(sensor, sensor_type):
                sensor_list.append(sensor)

        return sensor_list

    # =====================================================================================================

    def init_all_sensors(self, **kwargs) -> FunctionResult:
        """
        Initialize all sensors in the manager.

        Args:
            **kwargs: Additional keyword arguments for initialization.

        Returns:
            FunctionResult: The result of the initialization.
        """
        for sensor in self.sensors:
            result = sensor.init(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        for sensor in self.sensors:
            result = sensor.comm(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def check_all_sensors(self, **kwargs) -> FunctionResult:
        """
        Check all sensors in the manager.

        Args:
            **kwargs: Additional keyword arguments for checking.

        Returns:
            FunctionResult: The result of the check.
        """
        for sensor in self.sensors:
            retry_count = 0
            retry_max = 5
            result = FunctionResult.FAIL

            while retry_count < retry_max:
                result = sensor.check(**kwargs)
                if result == FunctionResult.SUCCESS:
                    break
                retry_count += 1

            if result != FunctionResult.SUCCESS:
                print(f"Sensor {sensor.id} check failed after {retry_count} retries.")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def subscribe_all_sensors(self, **kwargs) -> FunctionResult:
        """
        Subscribe all sensors in the manager.

        Args:
            **kwargs: Additional keyword arguments for subscribing.

        Returns:
            FunctionResult: The result of the subscription.
        """
        for sensor in self.sensors:
            result = sensor.subscribe(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def upload_all_sensors(self, **kwargs) -> FunctionResult:
        """
        Upload data from all sensors in the manager.

        Args:
            **kwargs: Additional keyword arguments for uploading.

        Returns:
            FunctionResult: The result of the upload.
        """
        for sensor in self.sensors:
            result = sensor.upload(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download_all_sensors(self, **kwargs) -> FunctionResult:
        """
        Download data to all sensors in the manager.

        Args:
            **kwargs: Additional keyword arguments for downloading.

        Returns:
            FunctionResult: The result of the download.
        """
        for sensor in self.sensors:
            result = sensor.download(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS
