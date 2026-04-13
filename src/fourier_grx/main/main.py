import os
import time
import traceback
import torch
import importlib.metadata

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.schedule import ischedule
from fourier_grx.predefine import (
    ControlSystemPeriod
)

__fourier_core_version__ = importlib.metadata.version("fourier_core")
__fourier_grx_version__ = importlib.metadata.version("fourier_grx")


def main():
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}#################################{PrintColor.RESET}")
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}Version Information:{PrintColor.RESET}")
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}fourier_core version: {__fourier_core_version__}{PrintColor.RESET}")
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}fourier_grx version: {__fourier_grx_version__}{PrintColor.RESET}")
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}eclipse-zenoh version: {importlib.metadata.version('eclipse-zenoh')}{PrintColor.RESET}")
    Logger().print_info(f"{PrintColor.LIGHT_YELLOW}#################################{PrintColor.RESET}")

    Logger().print_info("Process main start...")

    # 告知程序启动流程
    Logger().print_info("#################################")
    Logger().print_info("The program will start as follows:")
    Logger().print_info("1. Start the control thread.")
    Logger().print_info("2. Start the algorithm thread.")
    Logger().print_info("3. Start the communication thread.")
    Logger().print_info("4. The main program will start the scheduler.")
    Logger().print_info("If everything goes well, you can see 'You can start playing with the robot right now.'")
    Logger().print_info("(Message will be shown for 3 seconds.)")
    Logger().print_info("#################################")

    time.sleep(3)

    # --------------------------------------------------

    # FIXME: 开启 CPU 核心绑定会导致 pytorch 计算资源不足，因此暂时注释掉
    # 让程序在 CPU 0 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {0})

    # --------------------------------------------------

    from fourier_grx.license.fi_license import license_init

    # license_init()

    # --------------------------------------------------

    """
    Jason 2024-12-29:
    配置信息更新到全局配置中，建议在 main 函数中较早的位置进行配置信息的初始化
    """
    from fourier_core.config.fi_config import gl_config
    from fourier_grx.config.fi_config_validator import validate_config

    validate_config()

    # --------------------------------------------------

    from fourier_grx.comm import DynalinkManager

    DynalinkManager().dynalink_grx.fourier_core_version = __fourier_core_version__
    DynalinkManager().dynalink_grx.fourier_grx_version = __fourier_grx_version__

    DynalinkManager().dynalink_robot.robot_name = gl_config.parameters.get("robot", {}).get("name", "")

    # --------------------------------------------------
    # 子进程
    from fourier_grx.process import process_init, process_deinit

    process_init()

    # --------------------------------------------------
    # 子线程
    from fourier_grx.thread import thread_init, thread_deinit

    thread_init()

    # --------------------------------------------------

    # 设置 torch 线程数
    torch.set_grad_enabled(False)  # 禁用梯度计算，不进行用到 autograd 的计算图构建，节省内存和计算资源
    torch.set_num_threads(2)  # 设置 PyTorch 使用的线程数为 2，避免过多线程导致的资源竞争和性能下降
    torch.set_num_interop_threads(1)  # 设置 PyTorch 的线程池中用于并行计算的线程数为 1，进一步减少线程竞争

    # 控制定时器线程
    schedule_control_init()

    # 通信定时器线程
    schedule_communication_init()

    Logger().print_success("\033[1m" + "=" * 51 + "\033[0m")
    Logger().print_success("\033[1m" + "| You can start playing with the robot right now. |" + "\033[0m")
    Logger().print_success("\033[1m" + "=" * 51 + "\033[0m")

    # 主进程
    try:
        ischedule.run_loop()

    except (KeyboardInterrupt, SystemExit):
        Logger().print_info("main program KeyboardInterrupt...")

        # --------------------------------------------------
        # 子进程
        process_deinit()

        # --------------------------------------------------
        # 子线程
        thread_deinit()

        # --------------------------------------------------

    except Exception as e:
        Logger().print_error(f"main program exception: {e}")
        traceback.print_exc()

    # 主进程结束
    Logger().print_info("main program stop...")

    # FIXME: 2024-12-27
    #  use KeyboardInterrupt can not stop the program fluently
    #  The main program will be blocked by the schedule loop

    return FunctionResult.SUCCESS


# ----------------------------------------------------------------------------------------------------


def schedule_control_init() -> FunctionResult:
    from fourier_core.config.fi_config import gl_config
    from fourier_grx.control_system.fi_control_system import ControlSystem

    Logger().print_info("schedule_control start...")

    target_control_period_in_s = \
        gl_config.parameters.get("robot", {}).get("control_period",
                                                  ControlSystemPeriod.DEFAULT_CTRL_PERIOD)

    if gl_config.parameters.get("mode") == "debug":
        result = ControlSystem().debug_mode(control_period=target_control_period_in_s)
    elif gl_config.parameters.get("mode") == "release":
        result = ControlSystem().play_mode(control_period=target_control_period_in_s)
    else:
        # default with debug mode
        result = ControlSystem().debug_mode(control_period=target_control_period_in_s)

    if result != FunctionResult.SUCCESS:
        Logger().print_error("main.py thread_robot_control ControlSystem().debug_mode failed!!!")
        return FunctionResult.FAIL

    # start control loop
    ischedule.schedule(schedule_control, interval=target_control_period_in_s)

    Logger().print_info("schedule_control finish!")

    return FunctionResult.SUCCESS


def schedule_control():
    from fourier_grx.control_system.fi_control_system import ControlSystem

    ControlSystem().robot_control_loop_run()


def schedule_communication_init() -> FunctionResult:
    from fourier_core.config.fi_config import gl_config

    Logger().print_info("schedule_communication start...")

    enable = \
        gl_config.parameters.get("communication", {}).get("enable", False)
    target_comm_period_in_s = \
        gl_config.parameters.get("communication", {}).get("period", ControlSystemPeriod.DEFAULT_COMM_PERIOD)

    # start communication loop
    if enable:
        ischedule.schedule(schedule_communication, interval=target_comm_period_in_s)

    Logger().print_info("schedule_communication finish!")

    return FunctionResult.SUCCESS


def schedule_communication():
    from fourier_grx.control_system.fi_control_system import ControlSystem

    ControlSystem().robot_control_loop_communication()
