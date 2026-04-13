import socket
import traceback

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.comm.hex.fi_comm_protocol_hex import (
    CommProtocolHex,
)
from fourier_grx.comm.json.fi_comm_protocol_json_m4 import (
    CommProtocolJsonM4 as CommProtocolJson,
)
from fourier_grx.comm import *

gl_socket_hex_tcp: socket.socket = None
gl_socket_hex: socket.socket = None
gl_socket_json: socket.socket = None
gl_socket_dds: socket.socket = None
gl_socket_sim: socket.socket = None
gl_socket_zenoh: socket.socket = None
gl_socket_teleoperation: socket.socket = None


def thread_communication_hex_tcp(args):
    global gl_socket_hex_tcp

    Logger().print_debug("thread_communication_hex_tcp start...")

    gl_socket_hex_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_hex_server_address = ("0.0.0.0", 4196)

    gl_socket_hex_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    gl_socket_hex_tcp.bind(s_hex_server_address)
    gl_socket_hex_tcp.listen(1)

    while True:
        DynalinkManager().dynalink_comm.flag_ethernet_connect_status = FlagState.CLEAR

        client = None
        address = None

        try:
            Logger().print_debug("client is accept")
            client, address = gl_socket_hex_tcp.accept()  # 注意：阻塞方法， 用 ctrl+c 无法退出
            client.settimeout(2)

        except socket.timeout as e:
            Logger().print_debug("client is not accept")
            pass

        finally:
            pass

        if client is not None and address is not None:
            try:
                while True:
                    try:
                        data = client.recv(CommProtocolHex.RECEIVE_DATA_MAX_LENGTH)
                    except (OSError, socket.timeout) as e:
                        Logger().print_error(f"Socket recv error: {e}")
                        break

                    # 说明：当网络断开时，如果不对 client 进行关闭的话，会反复接收到 b"" 的空数据帧
                    if data is not None and data != b"":
                        # Logger().print_debug("client = ", client, " data.hex() = ", data.hex())

                        # socket client -> connector_hex
                        CommProtocolHex().receive(data)

                        Logger().print_debug("data except data.hex() = ", data.hex())
                    else:
                        Logger().print_debug("data close", data)
                        try:
                            client.close()
                            DynalinkManager().dynalink_comm.flag_ethernet_connect_status = FlagState.CLEAR
                        except OSError as e:
                            Logger().print_error(f"Socket close error: {e}")
                            break
                        break

            except ConnectionResetError as e:
                Logger().print_debug("ConnectionResetError close")
                client.close()

            except BrokenPipeError as e:
                Logger().print_debug("BrokenPipeError close")
                client.close()

            except Exception as e:
                traceback.print_exception(e)
                client.close()

            finally:
                Logger().print_debug("finally close")
                client.close()

    Logger().print_debug("thread_communication_hex stop...")


def thread_communication_hex(args):
    global gl_socket_hex

    Logger().print_debug("thread_communication_hex start...")

    gl_socket_hex = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_hex_server_address = ("0.0.0.0", 4197)
    gl_socket_hex.bind(s_hex_server_address)

    try:
        while True:
            data, addr = gl_socket_hex.recvfrom(CommProtocolHex.RECEIVE_DATA_MAX_LENGTH)

            Logger().print_debug(f"data except data.hex() = {data.hex()}")
            DynalinkManager().dynalink_comm.flag_ethernet_connect_status = FlagState.CLEAR
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        traceback.print_exception(e)

    Logger().print_debug(f"thread_communication_hex stop...")


def thread_communication_json(args):
    global gl_socket_json

    Logger().print_debug("thread_communication_json start...")

    gl_socket_json = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_json_server_address = ("0.0.0.0", 4198)
    gl_socket_json.bind(s_json_server_address)

    try:
        while True:
            data, addr = gl_socket_json.recvfrom(CommProtocolJson.RECEIVE_DATA_MAX_LENGTH)

            try:
                function_result = CommProtocolJson().receive(data)

                if function_result == FunctionResult.SUCCESS:
                    gl_socket_json.sendto(bytes(CommProtocolJson().send_data.encode()), addr)

            except (OSError, ValueError) as e:
                Logger().print_error(f"JSON communication error: {e}")
                break
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        traceback.print_exception(e)

    Logger().print_debug("thread_communication_json stop...")


def thread_communication_dds(args):
    global gl_socket_dds

    Logger().print_debug("thread_communication_dds start...")

    gl_socket_dds = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_dds_server_address = ("0.0.0.0", 4199)
    gl_socket_dds.bind(s_dds_server_address)

    while True:
        break

    Logger().print_debug("thread_communication_dds stop...")


def thread_communication_sim(args):
    global gl_socket_sim

    Logger().print_debug("thread_communication_sim start...")

    gl_socket_sim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_dds_server_address = ("0.0.0.0", 4200)
    gl_socket_sim.bind(s_dds_server_address)

    while True:
        break

    Logger().print_debug("thread_communication_sim stop...")


def thread_communication_zenoh(args):
    global gl_socket_zenoh

    Logger().print_debug("thread_communication_zenoh start...")

    gl_socket_zenoh = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_zenoh_server_address = ("0.0.0.0", 4201)
    gl_socket_zenoh.bind(s_zenoh_server_address)

    while True:
        break

    Logger().print_debug("thread_communication_zenoh stop...")


def thread_communication_teleoperation(args):
    global gl_socket_teleoperation

    Logger().print_debug("thread_communication_teleoperation start...")

    gl_socket_teleoperation = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_teleoperation_server_address = ("0.0.0.0", 4202)
    gl_socket_teleoperation.bind(s_teleoperation_server_address)

    while True:
        break

    Logger().print_debug("thread_communication_zenoh stop...")
