from abc import ABC, abstractmethod
from fourier_core.predefine import *


class ActuatorBase(ABC):
    """
    ActuatorBase 是针对执行器的基类，所有执行器都需要继承该类，并实现其中的抽象方法：
    - init
    - comm
    - check
    - upload
    - download
    """

    def __init__(self, id="", config_key="actuator_base", **kwargs):
        self.id: str = id
        self.config_key = config_key

    def init(self, **kwargs) -> FunctionResult:
        """
        Init actuator
        初始化执行器

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    def comm(self, **kwargs) -> FunctionResult:
        """
        Comm actuator setup
        通信功能设置

        Args:
            **kwargs:

        Returns:

        """

        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        """
        Check actuator connected and ready
        检查执行器是否连接并准备就绪

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
        上传执行器数据

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
