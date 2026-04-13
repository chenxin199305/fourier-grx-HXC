import time
from multiprocessing import Process

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import (
    ControlSystemPeriod,
)

process_streamlit_process = None


def process_streamlit_init() -> FunctionResult:
    """
    初始化通信进程
    """
    global process_streamlit_process

    if gl_config.parameters.get("streamlit", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_streamlit_init start...")

    # 创建子进程
    if process_streamlit_process:
        """
        Jason 2025-12-10:
        关键在于 Python 多进程的启动方式以及内存隔离机制。
        | 启动方式        | 操作系统        | 行为         | 全局变量状态          |
        | ----------- | ----------- | ---------- | --------------- |
        | `fork` (默认) | Linux/macOS | 子进程复制父进程内存 | **继承父进程所有全局变量** |
        | `spawn`     | Windows/可配置 | 子进程重新加载模块  | 重置为模块定义时的初始值    |
        """
        process_streamlit_process = Process(
            target=process_streamlit,
        )
        process_streamlit_process.start()

    # 等待子进程启动
    time.sleep(1)

    Logger().print_debug("process_streamlit_init finish!")

    return FunctionResult.SUCCESS


def process_streamlit_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    global process_streamlit_process

    if gl_config.parameters.get("streamlit", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug(f"process_streamlit_deinit start...")

    # 释放子进程
    if process_streamlit_process is not None:
        process_streamlit_process.terminate()
        process_streamlit_process.join()
        process_streamlit_process = None

    Logger().print_debug(f"process_streamlit_deinit finish!")

    return FunctionResult.SUCCESS


# 子进程调用程序
def process_streamlit() -> FunctionResult:
    # update Logger id
    Logger().update_id(id="streamlit")

    Logger().print_debug("process_streamlit start...")

    # ------------------------------

    # 让程序在 CPU 4 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {4})

    # ------------------------------

    # 利用 bash 脚本启动 streamlit ...

    target_streamlit_update_period_in_s = \
        gl_config.parameters.get("streamlit", {}).get("period", ControlSystemPeriod.DEFAULT_STREAMLIT_PERIOD)

    while True:
        # 更新数据到 streamlit
        time.sleep(target_streamlit_update_period_in_s)

    Logger().print_debug("process_streamlit stop...")

    return FunctionResult.SUCCESS
