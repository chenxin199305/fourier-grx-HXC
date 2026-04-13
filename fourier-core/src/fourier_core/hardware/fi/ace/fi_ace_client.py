try:
    import fi_ace
except Exception as e:
    pass

import time
import traceback

from threading import Thread

from .fi_ace_logger import Logger
from .fi_ace_predefine import (
    FunctionResult,
    ACEModeOfOperation,
)
from .fi_ace_model import (
    NormalACE,
    DoubleBufferACE,
    gl_ace_model_group,
)
from .fi_ace_device import (
    gl_ace_intf_group,
)


# ---------------------------------------------------------------------------------------------------------------------

def set_enable(server_ip):
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    gl_ace_intf_group.device_map[server_ip].EnableControl(ctrl_mode=fi_ace.ctrl_mode_e.NONE, timeout_ms=1000, max_retry=5)
    return FunctionResult.SUCCESS


def set_disable(server_ip):
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    gl_ace_intf_group.device_map[server_ip].DisableControl()
    return FunctionResult.SUCCESS


def set_pd_mode(server_ip):
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    print(
        f"set_pd_mode\n"
        f"control_mode={fi_ace.ctrl_mode_e.PD_MODE}\n"
    )

    ret = gl_ace_intf_group.device_map[server_ip].EnableControl(ctrl_mode=fi_ace.ctrl_mode_e.PD_MODE, timeout_ms=1000, max_retry=5)

    print(
        f"ret = {ret}"
    )

    return FunctionResult.SUCCESS


def set_velocity_mode(server_ip, use_torque_sensor=False):
    """Enable velocity control mode.

    Args:
        server_ip: ACE device identifier.
        use_torque_sensor: If True, use VELOCITY_MODE_T (torque-sensor / non-linear torque fitting);
                           if False (default), use VELOCITY_MODE_C (current / linear torque fitting).
    """
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    ctrl_mode = fi_ace.ctrl_mode_e.VELOCITY_MODE_T if use_torque_sensor else fi_ace.ctrl_mode_e.VELOCITY_MODE_C

    print(
        f"set_velocity_mode\n"
        f"control_mode={ctrl_mode}\n"
    )

    ret = gl_ace_intf_group.device_map[server_ip].EnableControl(ctrl_mode=ctrl_mode, timeout_ms=1000, max_retry=5)

    print(
        f"ret = {ret}"
    )

    return FunctionResult.SUCCESS


def set_mode_of_operation(server_ip, mode_of_operation):
    if (
            mode_of_operation == ACEModeOfOperation.POSITION_CONTROL or
            mode_of_operation == ACEModeOfOperation.TORQUE_CONTROL or
            mode_of_operation == ACEModeOfOperation.CURRENT_CONTROL
    ):
        pass
    elif mode_of_operation == ACEModeOfOperation.VELOCITY_CONTROL:
        return set_velocity_mode(server_ip)
    elif mode_of_operation == ACEModeOfOperation.PD_CONTROL:
        return set_pd_mode(server_ip)
    else:
        pass

    return None


def set_pd_control(server_ip, position=None, velocity=None):
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    if position is None:
        position = 0

    if velocity is None:
        velocity = 0

    gl_ace_intf_group.device_map[server_ip].SetPDPositionVelocityNoAck(p_rad=position, v_radps=velocity)
    return FunctionResult.SUCCESS


def set_pd_param(server_ip, pd_control_kp, pd_control_kd):
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    param = fi_ace.param_t()
    param.type = fi_ace.param_type_e.PD_KP
    param.value = pd_control_kp
    gl_ace_intf_group.device_map[server_ip].SetParam(param=param)

    param = fi_ace.param_t()
    param.type = fi_ace.param_type_e.PD_KD
    param.value = pd_control_kd
    gl_ace_intf_group.device_map[server_ip].SetParam(param=param)

    return FunctionResult.SUCCESS


def set_velocity_control(server_ip, velocity=None, torque_ff=None):
    """Send a velocity target (no-ack) to the ACE device.

    Args:
        server_ip: ACE device identifier.
        velocity:  Target velocity in rad/s (defaults to 0).
        torque_ff: Feed-forward torque in N·m (defaults to 0).
    """
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    if velocity is None:
        velocity = 0.0
    if torque_ff is None:
        torque_ff = 0.0

    gl_ace_intf_group.device_map[server_ip].SetVelocityNoAck(v_radps=velocity, t_ff_Nm=torque_ff)
    return FunctionResult.SUCCESS


def set_velocity_param(server_ip, velocity_control_kp, velocity_control_ki, use_torque_sensor=False):
    """Set velocity controller gains (kp and ki) on the ACE device.

    Args:
        server_ip:            ACE device identifier.
        velocity_control_kp:  Proportional gain.
        velocity_control_ki:  Integral gain.
        use_torque_sensor:    If True, write V_KP_T / V_KI_T (torque-sensor variant);
                              if False (default), write V_KP_C / V_KI_C (current variant).
    """
    if gl_ace_intf_group.device_map.get(server_ip, None) is None:
        return FunctionResult.SUCCESS

    kp_type = fi_ace.param_type_e.V_KP_T if use_torque_sensor else fi_ace.param_type_e.V_KP_C
    ki_type = fi_ace.param_type_e.V_KI_T if use_torque_sensor else fi_ace.param_type_e.V_KI_C

    param = fi_ace.param_t()
    param.type = kp_type
    param.value = velocity_control_kp
    gl_ace_intf_group.device_map[server_ip].SetParam(param=param)

    param = fi_ace.param_t()
    param.type = ki_type
    param.value = velocity_control_ki
    gl_ace_intf_group.device_map[server_ip].SetParam(param=param)

    return FunctionResult.SUCCESS


# ---------------------------------------------------------------------------------------------------------------------

def get_pvc(server_ip):
    position = None
    velocity = None
    current = None
    timeout = 0

    position, velocity, current = gl_ace_model_group.ace_map[server_ip].get_pvc()
    timeout = gl_ace_model_group.ace_map[server_ip].get_timeout()

    return position, velocity, current, timeout


def get_pvct(server_ip):
    position = None
    velocity = None
    current = None
    torque = None
    timeout = 0

    position, velocity, current, torque = gl_ace_model_group.ace_map[server_ip].get_pvct()
    timeout = gl_ace_model_group.ace_map[server_ip].get_timeout()

    return position, velocity, current, torque, timeout


def get_error(server_ip):
    error_code = None
    timeout = 0

    error_code = gl_ace_model_group.ace_map[server_ip].get_error_code()
    timeout = gl_ace_model_group.ace_map[server_ip].get_timeout()

    return error_code, timeout


# ---------------------------------------------------------------------------------------------------------------------

def get_subs_data(server_ip):
    rx_pvctte = fi_ace.pvctte_t()
    ret = gl_ace_intf_group.device_map[server_ip].GetPVCTTe(rx_pvctte)

    if ret != fi_ace.ret_e.SUCCESS:
        return None

    return rx_pvctte


def thread_ace_client(check_frequency):
    """
    子线程接收 socket 数据
    (运行在主进程中）

    :param server_ips: 服务器 IP 地址（数组）
    :param check_frequency: 是否检查频率
    """
    global gl_ace_client_thread_server_ips

    Logger().print_info(f"thread_ace_client 子线程 \n"
                        f"check_frequency = {check_frequency}")

    current_time = time.time()
    receive_count = 0

    # 数据接收
    while True:
        try:
            # 更新 ACE 数据
            for server_ip in gl_ace_client_thread_server_ips:
                subs_data = get_subs_data(server_ip)
                if subs_data is None:
                    continue

                # print(
                #     f"subs_data = {subs_data}\n"
                #     f"subs_data.pos = {subs_data.pos}\n"
                #     f"subs_data.vel = {subs_data.vel}\n"
                #     f"subs_data.cur = {subs_data.cur}\n"
                #     f"subs_data.tor = {subs_data.tor}\n"
                # )

                ace = gl_ace_model_group.ace_map[server_ip]
                ace.update(
                    p=subs_data.pos,
                    v=subs_data.vel,
                    c=subs_data.cur,
                    t=subs_data.tor,
                    e=None,  # ace 没有 error 数据
                    o=None,  # ace 永远都不超时
                )
                ace.publish()

            # 检查频率
            if check_frequency:
                receive_count += 1

                # 每秒打印一次接收频率
                if time.time() - current_time >= 1:
                    Logger().print_info(f"子线程 thread_ace_client receive_count = {receive_count}")
                    receive_count = 0
                    current_time = time.time()

            time.sleep(0.0015)

        except KeyboardInterrupt:
            Logger().print_warning("fi_ace thread_ace_client KeyboardInterrupt")
            break

        except Exception as e:
            Logger().print_error(f"fi_ace thread_ace_client Except")
            traceback.print_exception(e)
            return FunctionResult.FAIL

    return FunctionResult.SUCCESS


gl_ace_ipc_inited_flag = False
gl_ace_client_thread = None
gl_ace_client_thread_server_ips = []


# ---------------------------------------------------------------------------------------------------------------------


def init(server_ip):
    gl_ace_model_group.add_ace(server_ip=server_ip,
                               ace=DoubleBufferACE(server_ip=server_ip))

    return FunctionResult.SUCCESS


def comm(server_ip, enable=True):
    global gl_ace_ipc_inited_flag

    # set comm enable flag
    gl_ace_model_group.ace_map[server_ip].comm_enable = enable

    # 去掉 comm_enable 为 false 的 server_ip, 只给 enable 的 server_ip 建立 ACE
    if enable:

        # 初始化 IPC（只需要初始化一次）
        if not gl_ace_ipc_inited_flag:
            if fi_ace.AC.EthercatIpcInit(read_only=False) == fi_ace.ret_e.SUCCESS:
                gl_ace_ipc_inited_flag = True
            else:
                Logger().print_error(f"{server_ip} fi_ace.AC.EthercatIpcInit() failed")

        # 添加 ACE 设备
        gl_ace_intf_group.add_device(server_ip=server_ip,
                                     device=fi_ace.AC())

        server_ip_int = int(server_ip)

        # 初始化 ACE 设备（通过别名）
        if gl_ace_intf_group.device_map[server_ip].InitByAlias(server_ip_int) != fi_ace.ret_e.SUCCESS:
            Logger().print_error(f"{server_ip} fi_ace.AC.InitByAlias() failed")
            return FunctionResult.FAIL

    return FunctionResult.SUCCESS


def check(server_ip):
    return FunctionResult.SUCCESS


def subscribe(server_ip, enable=True):
    global gl_ace_client_thread

    # 针对特定执行器的订阅使能
    if not gl_ace_model_group.ace_map[server_ip].comm_enable:
        return FunctionResult.SUCCESS

    # 创建子线程（用于接收订阅数据）
    check_frequency = False

    # 创建子线程（用于接收 socket 数据）
    if gl_ace_client_thread is None:
        gl_ace_client_thread = Thread(
            target=thread_ace_client,
            args=(check_frequency,),
        )
        gl_ace_client_thread.start()

        # 睡眠一段时间，等待子线程启动
        time.sleep(1.0)

    #
    gl_ace_client_thread_server_ips.append(server_ip)

    return FunctionResult.SUCCESS
