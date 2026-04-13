import os
import json
import time
import traceback
from multiprocessing import Process
import numpy

import scipy
from scipy.spatial.transform import Rotation as R

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *
from fourier_core.predefine import (
    FunctionResult,
)

from fourier_grx.comm import (
    DynalinkManager,
)
from fourier_grx.process.sync.fi_sync_client import (
    SyncClient,
)

# Global variables to hold the process and interfaces
teleoperation_process = None

yup_to_zup_matrix = numpy.array([[0, -1, 0], [0, 0, 1], [1, 0, 0]])
wrist_to_pico_matrix = numpy.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])


def process_teleoperation_init() -> FunctionResult:
    """
    Initialize the teleoperation process and related resources.
    """
    global teleoperation_process

    if gl_config.parameters.get("teleoperation", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_teleoperation_init start...")

    # 创建子进程
    if teleoperation_process is None:
        """
        Jason 2025-12-10:
        关键在于 Python 多进程的启动方式以及内存隔离机制。
        | 启动方式        | 操作系统        | 行为         | 全局变量状态          |
        | ----------- | ----------- | ---------- | --------------- |
        | `fork` (默认) | Linux/macOS | 子进程复制父进程内存 | **继承父进程所有全局变量** |
        | `spawn`     | Windows/可配置 | 子进程重新加载模块  | 重置为模块定义时的初始值    |
        """
        teleoperation_process = Process(
            target=process_teleoperation
        )
        teleoperation_process.start()

    # 等待子进程启动
    time.sleep(1)

    Logger().print_debug("process_teleoperation_init finish!")

    return FunctionResult.SUCCESS


def process_teleoperation_deinit() -> FunctionResult:
    """
    Deinitialize the teleoperation process and related resources.
    """
    global teleoperation_process

    if gl_config.parameters.get("teleoperation", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    Logger().print_debug("process_teleoperation_deinit start...")

    if teleoperation_process is not None:
        teleoperation_process.terminate()
        teleoperation_process.join()
        teleoperation_process = None

    Logger().print_debug("process_teleoperation_deinit finish!")

    return FunctionResult.SUCCESS


def process_teleoperation() -> FunctionResult:
    """
    The main function for processing teleoperation.
    """
    # update Logger id
    Logger().update_id(id="teleoperation")

    Logger().print_debug("process_teleoperation start...")

    # ------------------------------

    # 让程序在 CPU 4 上运行
    # pid = os.getpid()
    # os.sched_setaffinity(pid, {4})

    # ------------------------------

    # create zenoh session
    import zenoh

    zenoh_config = zenoh.Config()
    session_teleoperation = zenoh.open(zenoh_config)

    teleoperation_key = "fourier_grx/teleoperation/sub"

    def listener(sample: zenoh.Sample):
        json_data = sample.payload.to_string().strip().strip('\x00')

        try:
            data = json.loads(json_data)

            # command = data.get("command")
            # if command == "UpControl":
            #     left_arm_control(data["data"]["left"]["hand"])
            #     right_arm_control(data["data"]["right"]["hand"])

            left_arm_control(data["left"]["hand"])
            right_arm_control(data["right"]["hand"])
            head_control(data["head"])

            sync_client = SyncClient()
            sync_client.publish(
                key="grx",
                value={
                    "virtual_teleoperation_left_handle_pose":
                        DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose,
                    "virtual_teleoperation_right_handle_pose":
                        DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose,
                    "virtual_teleoperation_head_pose":
                        DynalinkManager().dynalink_grx.virtual_teleoperation_head_pose,
                }
            )

        except json.JSONDecodeError as e:
            Logger().print_error(f"JSON Decode Error: {e} with data: {repr(json_data)}")

    sub = session_teleoperation.declare_subscriber(teleoperation_key, listener)

    try:
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        traceback.print_exception(e)
    finally:
        sub.undeclare()

        session_teleoperation.close()

    Logger().print_debug("process_teleoperation stop...")

    return FunctionResult.SUCCESS


def head_control(params):
    """
    Control the head position based on the provided parameters.
    """
    DynalinkManager().dynalink_grx.virtual_teleoperation_head_pose[:3] = [
        params.get(key) for key in ("r", "p", "y")
    ]

    if gl_config.parameters.get("teleoperation", {}).get("debug", False):
        Logger().print_debug(
            f"Head Control Parameters: {DynalinkManager().dynalink_grx.virtual_teleoperation_head_pose}"
        )


def left_arm_control(params):
    DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[:7] = [
        params.get(key) for key in ("x", "y", "z", "qw", "qx", "qy", "qz")
    ]

    if gl_config.parameters.get("teleoperation", {}).get("hardware_type", "UNKNOWN") == "Pico":
        pico_left_pose = DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose
        pico_left_quaternion = [pico_left_pose[4], pico_left_pose[5], pico_left_pose[6], pico_left_pose[3]]
        pico_left_rotation = R.from_quat(pico_left_quaternion)
        pico_left_matrix = pico_left_rotation.as_matrix()
        left_updated_quaternion = R.from_matrix(numpy.linalg.inv(yup_to_zup_matrix) @ pico_left_matrix @ (numpy.linalg.inv(yup_to_zup_matrix).T))
        quaternion_left_updated_quat = left_updated_quaternion.as_quat()
        DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[3] = quaternion_left_updated_quat[3]
        DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[4] = quaternion_left_updated_quat[0]
        DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[5] = quaternion_left_updated_quat[1]
        DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[6] = quaternion_left_updated_quat[2]

    if gl_config.parameters.get("teleoperation", {}).get("debug", False):
        Logger().print_debug(
            f"Left Arm Control Parameters: {DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose}"
        )


def right_arm_control(params):
    DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[:7] = [
        params.get(key) for key in ("x", "y", "z", "qw", "qx", "qy", "qz")
    ]

    if gl_config.parameters.get("teleoperation", {}).get("hardware_type", "UNKNOWN") == "Pico":
        pico_right_pose = DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose
        pico_right_quaternion = [pico_right_pose[4], pico_right_pose[5], pico_right_pose[6], pico_right_pose[3]]
        pico_right_rotation = R.from_quat(pico_right_quaternion)
        pico_right_matrix = pico_right_rotation.as_matrix()
        right_updated_quaternion = R.from_matrix(numpy.linalg.inv(yup_to_zup_matrix) @ pico_right_matrix @ (numpy.linalg.inv(yup_to_zup_matrix).T))
        quaternion_right_updated_quat = right_updated_quaternion.as_quat()
        DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[3] = quaternion_right_updated_quat[3]
        DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[4] = quaternion_right_updated_quat[0]
        DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[5] = quaternion_right_updated_quat[1]
        DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[6] = quaternion_right_updated_quat[2]

    if gl_config.parameters.get("teleoperation", {}).get("debug", False):
        Logger().print_debug(
            f"Right Arm Control Parameters: {DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose}"
        )


def upbody_control(params):
    DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose[:7] = [
        params.get(key) for key in ("x", "y", "z", "qw", "qx", "qy", "qz")
    ]
    DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose[:7] = [
        params.get(key) for key in ("x", "y", "z", "qw", "qx", "qy", "qz")
    ]

    if gl_config.parameters.get("teleoperation", {}).get("debug", False):
        pass
    else:
        Logger().print_debug(
            f"Left Arm Control Parameters: {DynalinkManager().dynalink_grx.virtual_teleoperation_left_handle_pose}"
        )
        Logger().print_debug(
            f"Right Arm Control Parameters: {DynalinkManager().dynalink_grx.virtual_teleoperation_right_handle_pose}"
        )


if __name__ == "__main__":
    process_teleoperation_init()

    try:
        while True:
            time.sleep(9999)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        traceback.print_exception(e)

    process_teleoperation_deinit()
