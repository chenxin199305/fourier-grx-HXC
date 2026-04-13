from enum import Enum

try:
    from fourier_core.predefine import FunctionResult
except ImportError:
    class FunctionResult(Enum):
        SUCCESS = 0
        FAIL = -1
        RUNNING = 1
        PREPARE = 2
        EXECUTE = 3
        NOT_EXECUTE = 4
        TIMEOUT = 5
        NOT_IMPLEMENTED = 6

try:
    from fourier_core.predefine import FlagState
except ImportError:
    class FlagState:
        CLEAR = 0
        SET = 1

try:
    from fourier_core.predefine.hardware.fi_hardware_type import HardwareType
except ImportError:
    class HardwareType(Enum):
        Base = "Base"
        Disconnect = "Disconnect"
        X64 = "X64"
