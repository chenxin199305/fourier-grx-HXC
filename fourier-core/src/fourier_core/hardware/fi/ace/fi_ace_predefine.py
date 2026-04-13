try:
    from fourier_core.predefine import FunctionResult
except ImportError:

    class FunctionResult:
        SUCCESS = 0
        FAIL = -1
        RUNNING = 1
        PREPARE = 2
        EXECUTE = 3
        NOT_EXECUTE = 4
        TIMEOUT = 5


class ACEModeOfOperation:
    NONE = 0
    TORQUE_CONTROL = 0
    CURRENT_CONTROL = 1
    VELOCITY_CONTROL = 2
    POSITION_CONTROL = 3
    PD_CONTROL = 4
