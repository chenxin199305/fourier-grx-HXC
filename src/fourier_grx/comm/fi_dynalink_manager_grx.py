from typing import Dict, Any, Optional
from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_grx import DynalinkGRX
from fourier_grx.comm.fi_dynalink_rehab import DynalinkRehab
from fourier_grx.comm.fi_dynalink_ros import DynalinkROS
from fourier_grx.comm.fi_dynalink_manager import DynalinkManager


class DynalinkManagerGRX(DynalinkManager):
    def _create_components(self) -> None:
        super()._create_components()

        if not hasattr(self, "dynalink_grx"):
            self.dynalink_grx: Optional[DynalinkGRX] = DynalinkGRX()

        if not hasattr(self, "dynalink_rehab"):
            self.dynalink_rehab: Optional[DynalinkRehab] = DynalinkRehab()

        if not hasattr(self, "dynalink_ros"):
            self.dynalink_ros: Optional[DynalinkROS] = DynalinkROS()

    def init(self, **kwargs):
        """
        Initialize the DynalinkManagerGRX components.
        """
        super().init(**kwargs)

        if self.dynalink_grx is not None:
            self.dynalink_grx.init(**kwargs)

        if self.dynalink_rehab is not None:
            self.dynalink_rehab.init(**kwargs)

        if self.dynalink_ros is not None:
            self.dynalink_ros.init(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        dynalink_dict: Dict[str, Any] = super().to_dict()

        if self.dynalink_grx is not None:
            dynalink_dict["dynalink_grx"] = self.dynalink_grx.to_dict()

        if self.dynalink_rehab is not None:
            dynalink_dict["dynalink_rehab"] = self.dynalink_rehab.to_dict()

        if self.dynalink_ros is not None:
            dynalink_dict["dynalink_ros"] = self.dynalink_ros.to_dict()

        return dynalink_dict

    def from_dict(self, dict_value: Optional[Dict[str, Any]]) -> FunctionResult:
        if super().from_dict(dict_value) == FunctionResult.FAIL:
            return FunctionResult.FAIL

        if dict_value is None:
            return FunctionResult.FAIL

        if "dynalink_grx" in dict_value:
            self.dynalink_grx.from_dict(dict_value["dynalink_grx"])

        if "dynalink_rehab" in dict_value:
            self.dynalink_rehab.from_dict(dict_value["dynalink_rehab"])

        if "dynalink_ros" in dict_value:
            self.dynalink_ros.from_dict(dict_value["dynalink_ros"])

        return FunctionResult.SUCCESS

    def read_to_dict(self) -> Dict[str, Any]:
        dynalink_read_dict: Dict[str, Any] = super().read_to_dict()

        if self.dynalink_grx is not None:
            dynalink_read_dict["dynalink_grx"] = self.dynalink_grx.read_to_dict()

        if self.dynalink_rehab is not None:
            dynalink_read_dict["dynalink_rehab"] = self.dynalink_rehab.read_to_dict()

        if self.dynalink_ros is not None:
            dynalink_read_dict["dynalink_ros"] = self.dynalink_ros.read_to_dict()

        return dynalink_read_dict

    def read_from_dict(self, dict_value: Optional[Dict[str, Any]]) -> FunctionResult:
        if super().read_from_dict(dict_value) == FunctionResult.FAIL:
            return FunctionResult.FAIL

        if dict_value is None:
            return FunctionResult.FAIL

        if "dynalink_grx" in dict_value:
            self.dynalink_grx.read_from_dict(dict_value["dynalink_grx"])

        if "dynalink_rehab" in dict_value:
            self.dynalink_rehab.read_from_dict(dict_value["dynalink_rehab"])

        if "dynalink_ros" in dict_value:
            self.dynalink_ros.read_from_dict(dict_value["dynalink_ros"])

        return FunctionResult.SUCCESS

    def write_to_dict(self) -> Dict[str, Any]:
        dynalink_write_dict: Dict[str, Any] = super().write_to_dict()

        if self.dynalink_grx is not None:
            dynalink_write_dict["dynalink_grx"] = self.dynalink_grx.write_to_dict()

        if self.dynalink_rehab is not None:
            dynalink_write_dict["dynalink_rehab"] = self.dynalink_rehab.write_to_dict()

        if self.dynalink_ros is not None:
            dynalink_write_dict["dynalink_ros"] = self.dynalink_ros.write_to_dict()

        return dynalink_write_dict

    def write_from_dict(self, dict_value: Optional[Dict[str, Any]] = None) -> FunctionResult:
        if super().write_from_dict(dict_value) == FunctionResult.FAIL:
            return FunctionResult.FAIL

        if dict_value is None:
            return FunctionResult.FAIL

        if "dynalink_grx" in dict_value:
            self.dynalink_grx.write_from_dict(dict_value["dynalink_grx"])

        if "dynalink_rehab" in dict_value:
            self.dynalink_rehab.write_from_dict(dict_value["dynalink_rehab"])

        if "dynalink_ros" in dict_value:
            self.dynalink_ros.write_from_dict(dict_value["dynalink_ros"])

        return FunctionResult.SUCCESS

    # =====================================================================================================
