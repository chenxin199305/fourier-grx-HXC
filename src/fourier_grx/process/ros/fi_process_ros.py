from fourier_core.predefine import *

process_ros_process = None


def process_ros_init() -> FunctionResult:
    """
    初始化通信进程
    """
    return FunctionResult.SUCCESS


def process_ros_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    return FunctionResult.SUCCESS


def disable_peripheral() -> FunctionResult:
    """
    Jason 2024-10-31:
    Disable peripheral, in avoid of having different process having the same peripheral.
    """
    return FunctionResult.SUCCESS


# 子进程调用程序
def process_ros() -> FunctionResult:
    return FunctionResult.SUCCESS
