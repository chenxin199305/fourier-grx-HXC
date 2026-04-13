from abc import ABC, abstractmethod
from fourier_core.predefine import *


class SensorBase(ABC):
    """
    ActuatorBase 是针对传感器的基类，所有传感器都需要继承该类，并实现其中的抽象方法：
    - init
    - comm
    - check
    - upload
    """

    def __init__(self, id="", config_key="sensor_base", **kwargs):
        self.id = id
        self.config_key = config_key

    def init(self, **kwargs) -> FunctionResult:
        """
        Init actuator

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    def comm(self, **kwargs) -> FunctionResult:
        """
        Comm actuator setup

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        """
        Check actuator connected and ready

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    def subscribe(self, **kwargs) -> FunctionResult:
        """
        Subscribe actuator data
        订阅执行器数据

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    # ------------------- Upload -------------------

    def upload(self, **kwargs) -> FunctionResult:
        """
        Upload actuator data

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    # ------------------- Upload -------------------

    # ------------------- Download -------------------

    def download(self, **kwargs) -> FunctionResult:
        """
        Download actuator data
        下发执行器数据

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    # ------------------- Download -------------------
