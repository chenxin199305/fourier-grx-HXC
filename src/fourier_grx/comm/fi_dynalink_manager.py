from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_comm import DynalinkComm
from fourier_grx.comm.fi_dynalink_core import DynalinkCore
from fourier_grx.comm.fi_dynalink_hardware import DynalinkHardware
from fourier_grx.comm.fi_dynalink_robot import DynalinkRobot
from fourier_grx.comm.fi_dynalink_task import DynalinkTask


class DynalinkManager:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __init__(self):
        pass

    def _create_components(self):
        if not hasattr(self, "dynalink_comm"):
            self.dynalink_comm = DynalinkComm()

        if not hasattr(self, "dynalink_core"):
            self.dynalink_core = DynalinkCore()

        if not hasattr(self, "dynalink_hardware"):
            self.dynalink_hardware = DynalinkHardware()

        if not hasattr(self, "dynalink_robot"):
            self.dynalink_robot = DynalinkRobot()

        if not hasattr(self, "dynalink_task"):
            self.dynalink_task = DynalinkTask()

    def init(self, **kwargs):
        """
        Initialize the DynalinkManager components.
        """
        if self.dynalink_comm is not None:
            self.dynalink_comm.init(**kwargs)

        if self.dynalink_core is not None:
            self.dynalink_core.init(**kwargs)

        if self.dynalink_hardware is not None:
            self.dynalink_hardware.init(**kwargs)

        if self.dynalink_robot is not None:
            self.dynalink_robot.init(**kwargs)

        if self.dynalink_task is not None:
            self.dynalink_task.init(**kwargs)

    def to_dict(self) -> dict:
        dynalink_dict = {}

        if self.dynalink_comm is not None:
            dynalink_dict["comm"] = self.dynalink_comm.to_dict()
        if self.dynalink_core is not None:
            dynalink_dict["core"] = self.dynalink_core.to_dict()
        if self.dynalink_hardware is not None:
            dynalink_dict["hardware"] = self.dynalink_hardware.to_dict()
        if self.dynalink_robot is not None:
            dynalink_dict["robot"] = self.dynalink_robot.to_dict()
        if self.dynalink_task is not None:
            dynalink_dict["task"] = self.dynalink_task.to_dict()

        return dynalink_dict

    def from_dict(self, dict_value) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        if "comm" in dict_value:
            self.dynalink_comm.from_dict(dict_value["comm"])
        if "core" in dict_value:
            self.dynalink_core.from_dict(dict_value["core"])
        if "hardware" in dict_value:
            self.dynalink_hardware.from_dict(dict_value["hardware"])
        if "robot" in dict_value:
            self.dynalink_robot.from_dict(dict_value["robot"])
        if "task" in dict_value:
            self.dynalink_task.from_dict(dict_value["task"])

        return FunctionResult.SUCCESS

    def read_to_dict(self) -> dict:
        dynalink_read_dict = {}

        if self.dynalink_comm is not None:
            dynalink_read_dict["comm"] = self.dynalink_comm.read_to_dict()
        if self.dynalink_core is not None:
            dynalink_read_dict["core"] = self.dynalink_core.read_to_dict()
        if self.dynalink_hardware is not None:
            dynalink_read_dict["hardware"] = self.dynalink_hardware.read_to_dict()
        if self.dynalink_robot is not None:
            dynalink_read_dict["robot"] = self.dynalink_robot.read_to_dict()
        if self.dynalink_task is not None:
            dynalink_read_dict["task"] = self.dynalink_task.read_to_dict()

        return dynalink_read_dict

    def read_from_dict(self, dict_value) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        if "comm" in dict_value:
            self.dynalink_comm.read_from_dict(dict_value["comm"])
        if "core" in dict_value:
            self.dynalink_core.read_from_dict(dict_value["core"])
        if "hardware" in dict_value:
            self.dynalink_hardware.read_from_dict(dict_value["hardware"])
        if "robot" in dict_value:
            self.dynalink_robot.read_from_dict(dict_value["robot"])
        if "task" in dict_value:
            self.dynalink_task.read_from_dict(dict_value["task"])

        return FunctionResult.SUCCESS

    def write_to_dict(self) -> dict:
        dynalink_write_dict = {}

        if self.dynalink_comm is not None:
            dynalink_write_dict["comm"] = self.dynalink_comm.write_to_dict()
        if self.dynalink_core is not None:
            dynalink_write_dict["core"] = self.dynalink_core.write_to_dict()
        if self.dynalink_hardware is not None:
            dynalink_write_dict["hardware"] = self.dynalink_hardware.write_to_dict()
        if self.dynalink_robot is not None:
            dynalink_write_dict["robot"] = self.dynalink_robot.write_to_dict()
        if self.dynalink_task is not None:
            dynalink_write_dict["task"] = self.dynalink_task.write_to_dict()

        return dynalink_write_dict

    def write_from_dict(self, dict_value=None) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        if "comm" in dict_value:
            self.dynalink_comm.write_from_dict(dict_value["comm"])
        if "core" in dict_value:
            self.dynalink_core.write_from_dict(dict_value["core"])
        if "hardware" in dict_value:
            self.dynalink_hardware.write_from_dict(dict_value["hardware"])
        if "robot" in dict_value:
            self.dynalink_robot.write_from_dict(dict_value["robot"])
        if "task" in dict_value:
            self.dynalink_task.write_from_dict(dict_value["task"])

        return FunctionResult.SUCCESS

    # =====================================================================================================
