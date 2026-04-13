import time
import traceback
from multiprocessing import Process

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import (
    ControlSystemPeriod,
)

process_dds_process = None


def process_dds_init() -> FunctionResult:
    """
    初始化通信进程
    """
    global process_dds_process

    if gl_config.parameters.get("dds", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_dds_init start...")

    # 创建子进程
    if process_dds_process is None:
        """
        Jason 2025-12-10:
        关键在于 Python 多进程的启动方式以及内存隔离机制。
        | 启动方式        | 操作系统        | 行为         | 全局变量状态          |
        | ----------- | ----------- | ---------- | --------------- |
        | `fork` (默认) | Linux/macOS | 子进程复制父进程内存 | **继承父进程所有全局变量** |
        | `spawn`     | Windows/可配置 | 子进程重新加载模块  | 重置为模块定义时的初始值    |
        """
        process_dds_process = Process(
            target=process_dds,
        )
        process_dds_process.start()

    # 等待子进程启动
    time.sleep(1)

    Logger().print_debug("process_dds_init finish!")

    return FunctionResult.SUCCESS


def process_dds_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    global process_dds_process

    if gl_config.parameters.get("dds", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug(f"process_dds_deinit start...")

    # 释放子进程
    if process_dds_process is not None:
        process_dds_process.terminate()
        process_dds_process.join()
        process_dds_process = None

    Logger().print_debug(f"process_dds_deinit finish!")

    return FunctionResult.SUCCESS


# 子进程调用程序
def process_dds() -> FunctionResult:
    """
    子进程主要执行内容
    """
    # update Logger id
    Logger().update_id(id="dds")

    Logger().print_debug("process_dds start...")

    # ------------------------------

    # 让程序在 CPU 4 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {4})

    # ------------------------------

    target_dds_update_period_in_s = \
        gl_config.parameters.get("dds", {}).get("period", ControlSystemPeriod.DEFAULT_DDS_PERIOD)

    # 初始化 DDSClient 进行数据同步
    from fourier_grx.process.dds.fi_dds_client import DDSClient

    Logger().print_debug("DDSClient() init...")

    DDSClient()

    Logger().print_success("DDSClient() finish!")

    try:
        while True:
            DDSClient().publish()

            time.sleep(target_dds_update_period_in_s)

    except KeyboardInterrupt:
        pass

    except SystemExit:
        pass

    except Exception as e:
        traceback.print_exception(e)

    Logger().print_debug("process_dds stop...")

    return FunctionResult.SUCCESS
