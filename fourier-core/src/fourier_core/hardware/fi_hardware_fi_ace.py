import numpy
from collections.abc import Iterable

from .fi_hardware_predefine import FunctionResult
from .fi_hardware_logger import Logger
from .fi_hardware_import import (
    fi_ace,
)


# -------------------------------------------------------------------------


def fi_ace_init(self, ip):
    Logger().print_info(f"FI ACE init: {ip}...")
    fi_ace.init(
        server_ip=ip,
    )

    return FunctionResult.SUCCESS


def fi_ace_comm(self, ip, enable=True):
    Logger().print_info(f"FI ACE comm: {ip}, enable={enable}...")
    fi_ace.comm(
        server_ip=ip,
        enable=enable,
    )

    return FunctionResult.SUCCESS


def fi_ace_check(self, ip):
    Logger().print_info(f"FI ACE check: {ip}...")
    result = fi_ace.check(
        server_ip=ip,
    )

    return result


def fi_ace_subscribe(self, ip, enable=False):
    Logger().print_info(f"FI ACE subscribe: {ip}, enable={enable}...")
    result = fi_ace.subscribe(server_ip=ip, enable=enable)

    return result


# -------------------------------------------------------------------------

def fi_ace_set_servo_on(self, ip):
    fi_ace.set_enable(
        server_ip=ip,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_servo_off(self, ip):
    fi_ace.set_disable(
        server_ip=ip,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_control_mode(self, ip, control_mode):
    fi_ace.set_mode_of_operation(
        server_ip=ip,
        mode_of_operation=control_mode,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_pd_control(self, ip, command_position=0, command_velocity=0):
    fi_ace.set_pd_control(
        server_ip=ip,
        position=command_position,
        velocity=command_velocity,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_pd_param(self, ip, pd_control_kp=None, pd_control_kd=None):
    fi_ace.set_pd_param(
        server_ip=ip,
        pd_control_kp=pd_control_kp,
        pd_control_kd=pd_control_kd,
    )

    return FunctionResult.SUCCESS


def fi_ace_get_pvc(self, ip):
    result = fi_ace.get_pvc(
        server_ip=ip,
    )

    position = None
    velocity = None
    current = None
    timeout = 0

    if result is not None and isinstance(result, Iterable):
        position, velocity, current, timeout = result
    else:
        timeout = 1

    return position, velocity, current, timeout


def fi_ace_get_pvct(self, ip):
    result = fi_ace.get_pvct(
        server_ip=ip,
    )

    position = None
    velocity = None
    current = None
    torque = None
    timeout = 0

    if result is not None and isinstance(result, Iterable):
        position, velocity, current, torque, timeout = result
    else:
        timeout = 1

    return position, velocity, current, torque, timeout


def fi_ace_get_error(self, ip):
    result = fi_ace.get_error(
        server_ip=ip,
    )

    error = None
    timeout = 0

    if result is not None and isinstance(result, Iterable):
        error, timeout = result
    else:
        timeout = 1

    return error, timeout


def fi_ace_set_control_pd(
        self,
        ip,
        pd_control_kp=None,
        pd_control_kd=None):
    result = fi_ace.set_pd_param_imm(
        server_ip=ip,
        pd_control_kp=pd_control_kp,
        pd_control_kd=pd_control_kd,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_velocity_control(self, ip, command_velocity=0, torque_ff=0):
    fi_ace.set_velocity_control(
        server_ip=ip,
        velocity=command_velocity,
        torque_ff=torque_ff,
    )

    return FunctionResult.SUCCESS


def fi_ace_set_velocity_param(self, ip, velocity_control_kp=None, velocity_control_ki=None):
    fi_ace.set_velocity_param(
        server_ip=ip,
        velocity_control_kp=velocity_control_kp,
        velocity_control_ki=velocity_control_ki,
    )

    return FunctionResult.SUCCESS

# -------------------------------------------------------------------------
