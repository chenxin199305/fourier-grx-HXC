from threading import Thread

from fourier_core.config.fi_config import gl_config
from fourier_core.predefine import *


def process_comm() -> FunctionResult:
    if gl_config.parameters.get("comm", {}).get("enable", False):
        pass
    else:
        return FunctionResult.SUCCESS

    # 初始化 comm
    from fourier_grx.process.comm.fi_process_comm_thread import (
        thread_communication_hex_tcp,
        thread_communication_hex,
        thread_communication_json,
        thread_communication_dds,
        thread_communication_sim,
        thread_communication_zenoh,
        thread_communication_teleoperation,
    )

    if gl_config.parameters.get("comm", {}).get("use_hex_tcp", False):
        tctl = Thread(target=thread_communication_hex_tcp, args=(1,), daemon=True, )
        tctl.start()

    if gl_config.parameters.get("comm", {}).get("use_hex", False):
        tcrl = Thread(target=thread_communication_hex, args=(1,), daemon=True, )
        tcrl.start()

    if gl_config.parameters.get("comm", {}).get("use_json", False):
        tcjl = Thread(target=thread_communication_json, args=(1,), daemon=True, )
        tcjl.start()

    if gl_config.parameters.get("comm", {}).get("use_dds", False):
        tcdl = Thread(target=thread_communication_dds, args=(1,), daemon=True, )
        tcdl.start()

    if gl_config.parameters.get("comm", {}).get("use_sim", False):
        tcsl = Thread(target=thread_communication_sim, args=(1,), daemon=True, )
        tcsl.start()

    if gl_config.parameters.get("comm", {}).get("use_zenoh", False):
        tczl = Thread(target=thread_communication_zenoh, args=(1,), daemon=True, )
        tczl.start()

    if gl_config.parameters.get("comm", {}).get("use_teleoperation", False):
        tczl = Thread(target=thread_communication_teleoperation, args=(1,), daemon=True, )
        tczl.start()

    return FunctionResult.SUCCESS
