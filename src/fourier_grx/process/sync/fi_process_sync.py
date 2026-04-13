import time
import traceback
from multiprocessing import Process

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import (
    ControlSystemPeriod,
)

process_sync_process = None


def process_sync_init() -> FunctionResult:
    """
    初始化通信进程
    """
    global process_sync_process

    if gl_config.parameters.get("sync", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_sync_init start...")

    # 创建子进程
    if process_sync_process is None:
        """
        Jason 2025-12-10:
        关键在于 Python 多进程的启动方式以及内存隔离机制。
        | 启动方式        | 操作系统        | 行为         | 全局变量状态          |
        | ----------- | ----------- | ---------- | --------------- |
        | `fork` (默认) | Linux/macOS | 子进程复制父进程内存 | **继承父进程所有全局变量** |
        | `spawn`     | Windows/可配置 | 子进程重新加载模块  | 重置为模块定义时的初始值    |
        """
        process_sync_process = Process(
            target=process_sync,
        )
        process_sync_process.start()

    # 等待子进程启动
    time.sleep(1)

    Logger().print_debug("process_sync_init finish!")

    return FunctionResult.SUCCESS


def process_sync_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    global process_sync_process

    if gl_config.parameters.get("sync", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug(f"process_sync_deinit start...")

    # 释放子进程
    if process_sync_process is not None:
        process_sync_process.terminate()
        process_sync_process.join()
        process_sync_process = None

    Logger().print_debug(f"process_sync_deinit finish!")

    return FunctionResult.SUCCESS


# 子进程调用程序
def process_sync() -> FunctionResult:
    """
    子进程主要执行内容
    """
    # update Logger id
    Logger().update_id(id="sync")

    Logger().print_debug("process_sync start...")

    # ------------------------------

    # 让程序在 CPU 2 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {2})

    # ------------------------------

    target_sync_update_period_in_s = \
        gl_config.parameters.get("sync", {}).get("period", ControlSystemPeriod.DEFAULT_SYNC_PERIOD)

    # 初始化 SyncClient 进行数据同步
    from fourier_grx.process.sync.fi_sync_client import SyncClient

    Logger().print_debug("SyncClient() init...")

    SyncClient()

    Logger().print_success("SyncClient() finish!")

    # Comm 子线程 (用于从外部其他协议接收数据)
    from fourier_grx.process.comm.fi_process_comm import process_comm

    Logger().print_debug("process_comm() start...")

    process_comm()

    Logger().print_success("process_comm() finish!")

    try:
        while True:
            SyncClient().publish()

            time.sleep(target_sync_update_period_in_s)

    except KeyboardInterrupt:
        pass

    except SystemExit:
        pass

    except Exception as e:
        traceback.print_exception(e)

    Logger().print_debug("process_sync stop...")

    return FunctionResult.SUCCESS
