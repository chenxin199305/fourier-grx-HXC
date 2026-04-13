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

try:
    from fourier_core.predefine import FlagState
except ImportError:
    class FlagState:
        CLEAR = 0
        SET = 1
