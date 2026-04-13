import sys
import socket
import time
import msgpack
import traceback
import serial.tools.list_ports
import multiprocessing
from threading import Thread

from .forsense_logger import Logger
from .forsense_predefine import (
    FunctionResult,
    FlagState,
)
from .forsense_imu_usb_model import (
    NormalIMU,
    DoubleBufferIMU,
    gl_imu_group,
)
from .forsense_imu_usb_async_server import (
    process_usb_imu_forsense_server,
)


# ---------------------------------------------------------------------------------------------------------------------


def get_quat(usb_imu):
    quat = gl_imu_group.imu_map[usb_imu].get_quat()

    return quat


def get_angle(usb_imu):
    angle = gl_imu_group.imu_map[usb_imu].get_euler()

    return angle


def get_angular_velocity(usb_imu):
    angular_velocity = gl_imu_group.imu_map[usb_imu].get_gyro()

    return angular_velocity


def get_acceleration(usb_imu):
    acceleration = gl_imu_group.imu_map[usb_imu].get_accel()

    return acceleration


# ---------------------------------------------------------------------------------------------------------------------

def thread_usb_imu_forsense_client(sync_port, usb_imu, check_frequency=False):
    """
    子线程，用于接收 USB IMU Forsense 数据
    (运行在主进程中）

    :param sync_port: 同步服务端口
    :param usb_imu: USB IMU 设备
    :param check_frequency: 是否检查频率
    """

    Logger().print_info(f"thread_usb_imu_forsense_client 子线程 \n"
                        f"sync_port = {sync_port} \n"
                        f"usb_imu = {usb_imu} \n"
                        f"check_frequency = {check_frequency}")

    # 更新数据传输 socket 地址
    usb_imu_forsense_sync_socket_address = ("127.0.0.1", sync_port)

    # 创建数据传输 socket
    try:
        usb_imu_forsense_sync_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        usb_imu_forsense_sync_socket.bind(usb_imu_forsense_sync_socket_address)
        usb_imu_forsense_sync_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 512)

    except Exception as e:
        Logger().print_error(f"thread_usb_imu_forsense_client Except")
        traceback.print_exception(e)
        return FunctionResult.FAIL

    current_time = time.time()
    receive_count = 0

    # 数据接收
    while True:
        try:
            recv_data, _ = usb_imu_forsense_sync_socket.recvfrom(256)
            imu_data = msgpack.unpackb(recv_data, raw=False)

            # 更新 IMU 数据
            imu = gl_imu_group.imu_map.get(usb_imu)
            imu.update(
                quat=imu_data.get(usb_imu, {}).get("q"),
                euler=imu_data.get(usb_imu, {}).get("e"),
                gyro=imu_data.get(usb_imu, {}).get("g"),
                accel=imu_data.get(usb_imu, {}).get("a"),
            )
            imu.publish()

            # print(
            #     f"imu.quat = {imu.get_quat()}\n"
            #     f"imu.euler_angle = {imu.get_euler()}\n"
            #     f"imu.angular_velocity = {imu.get_gyro()}\n"
            #     f"imu.linear_acceleration = {imu.get_accel()}\n"
            # )

            # 检查频率
            if check_frequency:
                receive_count += 1

                # 每秒打印一次接收频率
                if time.time() - current_time >= 1:
                    Logger().print_info(f"子线程 usb_imu = {usb_imu} receive_count = {receive_count}")
                    receive_count = 0
                    current_time = time.time()

        except KeyboardInterrupt:
            Logger().print_warning(f"thread_usb_imu_forsense_client KeyboardInterrupt")
            break

        except Exception as e:
            Logger().print_error(f"thread_usb_imu_forsense_client Except")
            traceback.print_exception(e)
            return FunctionResult.FAIL


# ---------------------------------------------------------------------------------------------------------------------


def authorize(usb_imu):
    # device authentication
    # 1. check all usb devices
    import os
    import serial

    ports = [port.device for port in serial.tools.list_ports.comports() if "USB" in port.device]

    # 2. check if the usb device exist
    if usb_imu not in ports:
        Logger().print_error("USB not found: " + usb_imu)
        Logger().print_error("Please check the connection of the USB device!")
        return FunctionResult.FAIL

    # 3. call script to setup usb(/dev/ttyUSB0) authority
    Logger().print_info("sudo chmod 777 " + usb_imu)
    try:
        os.system("sudo chmod 777 " + usb_imu)
    except Exception as e:
        Logger().print_error("USB authority setup failed: " + str(e))
        return FunctionResult.FAIL

    return FunctionResult.SUCCESS


# ---------------------------------------------------------------------------------------------------------------------


def init(usb_imu):
    # create IMU object
    gl_imu_group.add_imu(usb=usb_imu,
                         imu=DoubleBufferIMU(usb=usb_imu))

    return FunctionResult.SUCCESS


def comm(usb_imu, enable=True, check_frequency=False):
    # set comm enable flag
    gl_imu_group.imu_map[usb_imu].comm_enable = enable
    gl_imu_group.imu_map[usb_imu].flag_thread_kill = not enable

    if enable:
        # TODO: change from len(gl_imu_od) to use index of the usb_imu
        usbs = [usb for usb in gl_imu_group.imu_map.keys() if gl_imu_group.imu_map[usb].comm_enable]

        usb_imu_index = 0
        for i in range(len(usbs)):
            if usb_imu == usbs[i]:
                usb_imu_index = i
                break

        sync_port = 20000 + usb_imu_index
        check_frequency = False

        # Forsense IMU 数据上传频率（单位：秒），默认为 500 Hz
        data_upload_period = 1.0 / 500.0

        # 授权
        if authorize(usb_imu) == FunctionResult.FAIL:
            sys.exit(FunctionResult.FAIL)

        # 创建子线程（用于接收 socket 数据）
        usb_imu_forsense_comm_thread = Thread(
            target=thread_usb_imu_forsense_client,
            args=(sync_port, usb_imu, check_frequency)
        )
        usb_imu_forsense_comm_thread.start()

        # 等待子线程启动
        time.sleep(1.0)

        # 创建子进程（用于发送 socket 数据）
        # spawn_ctx = multiprocessing.get_context('spawn')
        spawn_ctx = multiprocessing.get_context('fork')
        usb_imu_forsense_comm_process = spawn_ctx.Process(
            target=process_usb_imu_forsense_server,
            args=(sync_port, usb_imu, data_upload_period)
        )
        usb_imu_forsense_comm_process.start()

        # 等待子进程启动
        time.sleep(1.0)

    return FunctionResult.SUCCESS


def check(usb_imu):
    return FunctionResult.SUCCESS


def subscribe(usb_imu, enable=False):
    return FunctionResult.SUCCESS


def upload(usb_imu):
    # 更新放到子线程中...
    return FunctionResult.SUCCESS

# ---------------------------------------------------------------------------------------------------------------------
