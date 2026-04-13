from fourier_core.predefine import *

from fourier_grx.comm.fi_dynalink_protocol import (
    DynalinkProtocol,
)


class DynalinkBase(DynalinkProtocol):
    def _create_components(self):
        self.dict_fields: list = []
        self.read_fields: list = []
        self.write_fields: list = []

    def init(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.dict_fields}

    def from_dict(self, dict_value=None) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        for field in self.dict_fields:
            if field in dict_value:
                setattr(self, field, dict_value[field])

        return FunctionResult.SUCCESS

    def read_to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.read_fields}

    def read_from_dict(self, dict_value=None) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        for field in self.read_fields:
            if field in dict_value:
                setattr(self, field, dict_value[field])

        return FunctionResult.SUCCESS

    def write_to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.write_fields}

    def write_from_dict(self, dict_value=None) -> FunctionResult:
        if dict_value is None:
            return FunctionResult.FAIL

        for field in self.write_fields:
            if field in dict_value:
                setattr(self, field, dict_value[field])

        return FunctionResult.SUCCESS
