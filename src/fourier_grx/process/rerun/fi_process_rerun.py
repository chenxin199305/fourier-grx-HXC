import time
import traceback
from multiprocessing import Process

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import (
    ControlSystemPeriod,
)
from fourier_grx.comm import *

process_rerun_process = None


def process_rerun_init() -> FunctionResult:
    """
    初始化通信进程
    """
    global process_rerun_process

    if gl_config.parameters.get("rerun", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_rerun_init start...")

    # 创建子进程
    if process_rerun_process is None:
        """
        Jason 2025-12-10:
        关键在于 Python 多进程的启动方式以及内存隔离机制。
        | 启动方式        | 操作系统        | 行为         | 全局变量状态          |
        | ----------- | ----------- | ---------- | --------------- |
        | `fork` (默认) | Linux/macOS | 子进程复制父进程内存 | **继承父进程所有全局变量** |
        | `spawn`     | Windows/可配置 | 子进程重新加载模块  | 重置为模块定义时的初始值    |
        """
        process_rerun_process = Process(
            target=process_rerun,
        )
        process_rerun_process.start()

    # 等待子进程启动
    time.sleep(1)

    Logger().print_debug("process_rerun_init finish!")

    return FunctionResult.SUCCESS


def process_rerun_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    global process_rerun_process

    if gl_config.parameters.get("rerun", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug(f"process_rerun_deinit start...")

    # 释放子进程
    if process_rerun_process is not None:
        process_rerun_process.terminate()
        process_rerun_process.join()
        process_rerun_process = None

    Logger().print_debug(f"process_rerun_deinit finish!")

    return FunctionResult.SUCCESS


# 子进程调用程序
def process_rerun() -> FunctionResult:
    # update Logger id
    Logger().update_id(id="rerun")

    Logger().print_debug("process_rerun start...")

    # ------------------------------

    # 让程序在 CPU 4 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {4})

    # ------------------------------

    target_rerun_update_period_in_s = \
        gl_config.parameters.get("rerun", {}).get("period", ControlSystemPeriod.DEFAULT_RERUN_PERIOD)

    # 初始化 SyncClient 进行数据同步
    from fourier_grx.process.sync.fi_sync_client import SyncClient

    Logger().print_debug("SyncClient() start...")

    SyncClient()

    Logger().print_success("SyncClient() finish!")

    # 初始化 rerun
    import rerun

    Logger().print_debug("rerun.init() start...")

    """
    Jason 2025-06-29:
    使用 WebViewer 进行 rerun 的可视化，而不是 TCP。
    """
    rerun.init(application_id="fourier-grx", spawn=False, strict=False)
    rerun.serve_web(open_browser=gl_config.parameters.get("rerun", {}).get("open_browser", False))
    # rerun.connect_tcp()

    Logger().print_success("rerun.init() finish!")

    try:
        while True:
            # 更新数据到 rerun
            joint_measured_positions = DynalinkManager().dynalink_robot.joint_measured_position
            joint_measured_velocity = DynalinkManager().dynalink_robot.joint_measured_velocity
            joint_measured_effort = DynalinkManager().dynalink_robot.joint_measured_effort
            joint_measured_current = DynalinkManager().dynalink_robot.joint_measured_current

            joint_output_position = DynalinkManager().dynalink_robot.joint_output_position
            joint_output_velocity = DynalinkManager().dynalink_robot.joint_output_velocity
            joint_output_torque = DynalinkManager().dynalink_robot.joint_output_effort

            for i, position in enumerate(joint_measured_positions):
                rerun.log(f"joint_measured_positions/joint_{i}", rerun.Scalar(position))

            for i, velocity in enumerate(joint_measured_velocity):
                rerun.log(f"joint_measured_velocity/joint_{i}", rerun.Scalar(velocity))

            for i, effort in enumerate(joint_measured_effort):
                rerun.log(f"joint_measured_effort/joint_{i}", rerun.Scalar(effort))

            for i, current in enumerate(joint_measured_current):
                rerun.log(f"joint_measured_current/joint_{i}", rerun.Scalar(current))

            for i, position in enumerate(joint_output_position):
                rerun.log(f"joint_output_position/joint_{i}", rerun.Scalar(position))

            for i, velocity in enumerate(joint_output_velocity):
                rerun.log(f"joint_output_velocity/joint_{i}", rerun.Scalar(velocity))

            for i, torque in enumerate(joint_output_torque):
                rerun.log(f"joint_output_torque/joint_{i}", rerun.Scalar(torque))

            time.sleep(target_rerun_update_period_in_s)

    except KeyboardInterrupt:
        pass

    except SystemExit:
        pass

    except Exception as e:
        traceback.print_exception(e)

    rerun.rerun_shutdown()

    Logger().print_debug("process_rerun stop...")

    return FunctionResult.SUCCESS
