from fourier_core.predefine import *
from fourier_core.actuator.fi_actuator_base import ActuatorBase


class ActuatorManager:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls._instance.number_of_actuator = 0
            cls._instance.actuators = []

        return cls._instance

    def __str__(self):
        """
        打印 Manager 和 Actuator 的信息
        """
        info = f"ActuatorManager:\n"
        for actuator in self.actuators:
            info += f"  - {actuator.id}: {actuator}\n"
        return info

    def add_actuator(self, actuator: ActuatorBase) -> FunctionResult:
        if not isinstance(actuator, ActuatorBase):
            raise TypeError("actuator must be an instance of ActuatorBase")

        self.actuators.append(actuator)

        return FunctionResult.SUCCESS

    def remove_actuator(self, actuator: ActuatorBase):
        if not isinstance(actuator, ActuatorBase):
            raise TypeError("actuator must be an instance of ActuatorBase")

        if actuator in self.actuators:
            self.actuators.remove(actuator)
            return FunctionResult.SUCCESS

        return FunctionResult.FAIL

    def get_number_of_actuators(self, actuator_type=None) -> int:
        """
        获取传感器数量

        :param actuator_type: 传感器类型，必须是 ActuatorBase 的子类
        """
        # If no specific type is provided, return the total number of actuator
        if actuator_type is None:
            return len(self.actuators)

        # If a specific type is provided, count the actuator of that type
        number_of_actuators = 0

        for actuator in self.actuators:
            if isinstance(actuator, actuator_type):
                number_of_actuators += 1

        return number_of_actuators

    def get_actuator_list(self, actuator_type) -> list:
        """
        获取传感器列表

        :param actuator_type: 传感器类型，必须是 ActuatorBase 的子类
        """
        # If no specific type is provided, return all actuator
        if actuator_type is None:
            return self.actuators

        # If a specific type is provided, collect the actuator of that type
        actuator_list = []

        for actuator in self.actuators:
            if isinstance(actuator, actuator_type):
                actuator_list.append(actuator)

        return actuator_list

    # =====================================================================================================

    def init_all_actuators(self, **kwargs) -> FunctionResult:
        """
        Initialize all actuator in the manager.

        Args:
            **kwargs: Additional keyword arguments for initialization.

        Returns:
            FunctionResult: The result of the initialization.
        """

        for actuator in self.actuators:
            result = actuator.init(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        for actuator in self.actuators:
            result = actuator.comm(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def check_all_actuators(self, **kwargs) -> FunctionResult:
        """
        Check all actuator in the manager.

        Args:
            **kwargs: Additional keyword arguments for checking.

        Returns:
            FunctionResult: The result of the check.
        """
        for actuator in self.actuators:
            retry_count = 0
            retry_max = 5
            result = FunctionResult.FAIL

            while retry_count < retry_max:
                result = actuator.check(**kwargs)
                if result == FunctionResult.SUCCESS:
                    break
                retry_count += 1

            if result != FunctionResult.SUCCESS:
                print(f"Actuator {actuator.id} check failed after {retry_count} retries.")
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def subscribe_all_actuators(self, **kwargs) -> FunctionResult:
        """
        Subscribe all actuator in the manager.

        Args:
            **kwargs: Additional keyword arguments for subscribing.

        Returns:
            FunctionResult: The result of the subscription.
        """
        for actuator in self.actuators:
            result = actuator.subscribe(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def upload_all_actuators(self, **kwargs) -> FunctionResult:
        """
        Upload data from all actuator in the manager.

        Args:
            **kwargs: Additional keyword arguments for uploading.

        Returns:
            FunctionResult: The result of the upload.
        """
        for actuator in self.actuators:
            result = actuator.upload(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download_all_actuators(self, **kwargs) -> FunctionResult:
        """
        Download data to all actuator in the manager.

        Args:
            **kwargs: Additional keyword arguments for downloading.

        Returns:
            FunctionResult: The result of the download.
        """
        for actuator in self.actuators:
            result = actuator.download(**kwargs)
            if result != FunctionResult.SUCCESS:
                return FunctionResult.FAIL

        return FunctionResult.SUCCESS
