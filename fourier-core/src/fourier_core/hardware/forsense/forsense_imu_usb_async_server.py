import time
import socket
import numpy
import traceback
import msgpack
import serial
import serial.tools.list_ports
from queue import Queue
from ischedule import run_loop, schedule

from .forsense_logger import Logger
from .forsense_predefine import (
    FunctionResult,
    FlagState,
)
from .forsense_imu_usb_model import (
    NormalIMU,
    gl_imu_group,
)
from .forsense_protocol import (
    ForsenseFrame_NotCompleted_Exception,
    ForsenseFrame_ErrorFrame_Exception,
    intercept_one_complete_frame,
    extraction_information_from_frame,
    find_frame_header,
)

# ---------------------------------------------------------------------------------------------------------------------

# 全局变量（用于子进程）
gl_imu_sync_socket = None
gl_imu_sync_socket_address = None

gl_imu_usb_imu = None
gl_imu_serial = None
gl_imu_bin_buffer = None
gl_imu_fifo_buffer = None


def process_usb_imu_forsense_server(sync_port, usb_imu, data_upload_period=0.002):
    """
    子进程，用于发送 USB IMU Forsense 数据
    (运行在子进程中）
    """
    global \
        gl_imu_sync_socket, \
        gl_imu_sync_socket_address, \
        gl_imu_usb_imu, \
        gl_imu_serial, \
        gl_imu_bin_buffer, \
        gl_imu_fifo_buffer

    Logger().update_id("forsense_imu_server")

    Logger().print_info(f"process_usb_imu_forsense_server 子进程 \n"
                        f"sync_port = {sync_port} \n"
                        f"usb_imu = {usb_imu} \n"
                        f"data_upload_period = {data_upload_period}")

    # 更新数据传输 socket 地址
    gl_imu_sync_socket_address = ("127.0.0.1", sync_port)

    # 创建 IMU 数据对象
    gl_imu_usb_imu = usb_imu

    # 1. 初始化
    gl_imu_group.add_imu(usb_imu, NormalIMU(usb=usb_imu))

    # 2. 通信使能
    gl_imu_group.imu_map[usb_imu].comm_enable = True

    # 创建数据传输 socket
    try:
        gl_imu_sync_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    except Exception as e:
        Logger().print_error(f"process_usb_imu_forsense_server Except")
        return FunctionResult.FAIL

    # 打开串口
    try:
        gl_imu_serial = serial.Serial(port=usb_imu, baudrate=921600, timeout=1.0)

    except Exception as e:
        Logger().print_error(f"process_usb_imu_forsense_server Except")
        return FunctionResult.FAIL

    if gl_imu_serial.is_open:
        Logger().print_info(f"USB IMU Forsense {usb_imu} is already opened.")
    else:
        gl_imu_serial.open()

    # 配置缓冲区
    gl_imu_bin_buffer = []
    gl_imu_fifo_buffer = Queue()

    # 配置延时器
    target_read_data_period_in_s = data_upload_period  # update frequency
    Logger().print_info(f"子进程 upload_period = {target_read_data_period_in_s}")

    # 配置任务
    schedule(schedule_usb_imu_forsense_server, interval=target_read_data_period_in_s)

    # 启动调度器
    try:
        run_loop()
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except Exception as e:
        Logger().print_error(f"process_usb_imu_forsense_server Except")
        traceback.print_exception(e)

    # 关闭串口
    if gl_imu_serial.is_open:
        gl_imu_serial.close()
    else:
        Logger().print_info(f"USB IMU Forsense {usb_imu} is already closed.")

    # 关闭 socket
    if gl_imu_sync_socket is not None:
        gl_imu_sync_socket.close()

    return FunctionResult.SUCCESS


def schedule_usb_imu_forsense_server():
    """
    子进程，用于发送 USB IMU Forsense 数据
    (运行在子进程中）
    """
    global \
        gl_imu_sync_socket, \
        gl_imu_sync_socket_address, \
        gl_imu_usb_imu, \
        gl_imu_serial, \
        gl_imu_bin_buffer, \
        gl_imu_fifo_buffer

    usb_imu = gl_imu_usb_imu

    # 检查线程终止标志
    if gl_imu_group.imu_map[usb_imu].flag_thread_kill:
        return FunctionResult.FAIL

    # --------------------------------------------------------------------------------------------------------------

    # 读取数据
    try:
        # 获取串口缓冲区数据长度
        usb_imu_forsense_serial_buff_count = gl_imu_serial.in_waiting

    except Exception as e:
        Logger().print_error(f"schedule_usb_imu_forsense_server Except")
        return FunctionResult.FAIL

    # 解析数据
    if usb_imu_forsense_serial_buff_count > 0:
        # 读取串口缓冲区数据
        usb_imu_forsense_serial_buff = gl_imu_serial.read(usb_imu_forsense_serial_buff_count)

        # 将读取到的数据添加到全局缓冲区
        gl_imu_bin_buffer.extend(usb_imu_forsense_serial_buff)

        # 解析数据
        try:
            while True:
                # 嘗試查找完整幀,若失敗會拋出異常
                header_pos, end_pos = intercept_one_complete_frame(gl_imu_bin_buffer)

                # 解析完整幀
                extraction_information_from_frame(
                    gl_imu_bin_buffer[header_pos: end_pos + 1],
                    gl_imu_fifo_buffer,
                )

                gl_imu_bin_buffer = gl_imu_bin_buffer[end_pos + 1:]

        except ForsenseFrame_NotCompleted_Exception:
            # 接收進行中
            pass

        except ForsenseFrame_ErrorFrame_Exception as e:
            Logger().print_warning(e)

            # 目前幀有幀頭，但是為錯誤幀，跳過錯誤幀
            header_pos = find_frame_header(gl_imu_bin_buffer)
            gl_imu_bin_buffer = gl_imu_bin_buffer[header_pos + 1:]

    # --------------------------------------------------------------------------------------------------------------

    while not gl_imu_fifo_buffer.empty():
        usb_imu_forsense_fifobuffer_value = gl_imu_fifo_buffer.get(block=True, timeout=0.001)

        # 数据更新
        imu = gl_imu_group.imu_map.get(usb_imu)
        imu.measured_quat = [
            usb_imu_forsense_fifobuffer_value["quat"][0]["X"],
            usb_imu_forsense_fifobuffer_value["quat"][0]["Y"],
            usb_imu_forsense_fifobuffer_value["quat"][0]["Z"],
            usb_imu_forsense_fifobuffer_value["quat"][0]["W"],
        ]
        imu.measured_euler_angle = [
            usb_imu_forsense_fifobuffer_value["euler"][0]["Roll"],
            usb_imu_forsense_fifobuffer_value["euler"][0]["Pitch"],
            usb_imu_forsense_fifobuffer_value["euler"][0]["Yaw"],
        ]
        imu.measured_angular_velocity = [
            usb_imu_forsense_fifobuffer_value["gyr"][0]["X"],
            usb_imu_forsense_fifobuffer_value["gyr"][0]["Y"],
            usb_imu_forsense_fifobuffer_value["gyr"][0]["Z"],
        ]
        imu.measured_linear_acceleration = [
            usb_imu_forsense_fifobuffer_value["acc"][0]["X"],
            usb_imu_forsense_fifobuffer_value["acc"][0]["Y"],
            usb_imu_forsense_fifobuffer_value["acc"][0]["Z"],
        ]

        imu.measured_quat = numpy.round(imu.measured_quat, 3).tolist()
        imu.measured_euler_angle = numpy.round(imu.measured_euler_angle, 3).tolist()
        imu.measured_angular_velocity = numpy.round(imu.measured_angular_velocity, 3).tolist()
        imu.measured_linear_acceleration = numpy.round(imu.measured_linear_acceleration, 3).tolist()

        # print(
        #     f"imu.measured_quat = {imu.measured_quat}\n"
        #     f"imu.measured_euler_angle = {imu.measured_euler_angle}\n"
        #     f"imu.measured_angular_velocity = {imu.measured_angular_velocity}\n"
        #     f"imu.measured_linear_acceleration = {imu.measured_linear_acceleration}\n"
        # )

        # 推送数据
        try:
            send_data = {
                usb_imu: {
                    "q": imu.measured_quat,  # unit : none
                    "e": imu.measured_euler_angle,  # unit : deg
                    "g": imu.measured_angular_velocity,  # unit : deg/s
                    "a": imu.measured_linear_acceleration,  # unit : m/s^2
                }
            }

            gl_imu_sync_socket.sendto(
                msgpack.packb(send_data, use_bin_type=True),
                gl_imu_sync_socket_address
            )

        except Exception as e:
            Logger().print_error(f"schedule_usb_imu_forsense_server Except")
            return FunctionResult.FAIL

    return FunctionResult.SUCCESS

# ---------------------------------------------------------------------------------------------------------------------
