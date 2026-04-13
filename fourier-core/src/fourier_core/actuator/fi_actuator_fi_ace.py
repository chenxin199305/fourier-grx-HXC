import numpy
from collections.abc import Iterable

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.hardware.fi.ace.fi_ace_predefine import ACEModeOfOperation
from fourier_core.hardware import HardwareManager
from fourier_core.actuator.fi_actuator_motor import ActuatorMotor


class ActuatorFIACE(ActuatorMotor):
    def __init__(
            self,
            ip: str = "99",
            type: ActuatorFIACEType = ActuatorFIACEType.NONE
    ):
        super().__init__(
            id=ip,
            manufactor=ActuatorManufactor.FIACE,
            type=type
        )

        self.ip: str = ip
        self.comm_enable: bool = True

        self.control_mode_mapping_from_unified_to_specified = {
            ActuatorControlMode.NONE: ActuatorFIACEControlMode.NONE,
            ActuatorControlMode.CURRENT: ActuatorFIACEControlMode.CURRENT,
            ActuatorControlMode.EFFORT: ActuatorFIACEControlMode.EFFORT,
            ActuatorControlMode.VELOCITY: ActuatorFIACEControlMode.VELOCITY,
            ActuatorControlMode.POSITION: ActuatorFIACEControlMode.POSITION,
            ActuatorControlMode.TRAPEZOIDAL: ActuatorFIACEControlMode.POSITION,
            ActuatorControlMode.PD: ActuatorFIACEControlMode.PD,

            ActuatorControlMode.SERVO_ON: ActuatorFIACEControlMode.SERVO_ON,
            ActuatorControlMode.SERVO_OFF: ActuatorFIACEControlMode.SERVO_OFF,
            ActuatorControlMode.SERVO_REBOOT: ActuatorFIACEControlMode.SERVO_REBOOT,
            ActuatorControlMode.SERVO_ZERO: ActuatorFIACEControlMode.SERVO_ZERO,

            ActuatorControlMode.SET_PID: ActuatorFIACEControlMode.SET_PID,
            ActuatorControlMode.SET_PARAM: ActuatorFIACEControlMode.SET_PARAM,

            ActuatorControlMode.CLEAR_FAULT: ActuatorFIACEControlMode.CLEAR_FAULT,
        }

        self.mode_of_operation_mapping_from_control_mode = {
            ActuatorFIACEControlMode.CURRENT: ACEModeOfOperation.CURRENT_CONTROL,
            ActuatorFIACEControlMode.EFFORT: ACEModeOfOperation.TORQUE_CONTROL,
            ActuatorFIACEControlMode.VELOCITY: ACEModeOfOperation.VELOCITY_CONTROL,
            ActuatorFIACEControlMode.POSITION: ACEModeOfOperation.POSITION_CONTROL,
            ActuatorFIACEControlMode.PD: ACEModeOfOperation.PD_CONTROL,
        }

    def init(self, **kwargs) -> FunctionResult:
        HardwareManager().fi_ace_init(ip=self.ip)
        return FunctionResult.SUCCESS

    def comm(self, **kwargs) -> FunctionResult:
        self.comm_enable = kwargs.get("enable", True)
        HardwareManager().fi_ace_comm(ip=self.ip, enable=self.comm_enable)
        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        result = HardwareManager().fi_ace_check(ip=self.ip)
        return result

    def subscribe(self, **kwargs) -> FunctionResult:
        enable = kwargs.get("enable", False)
        result = HardwareManager().fi_ace_subscribe(ip=self.ip, enable=enable)
        return result

    def upload(self, **kwargs) -> FunctionResult:
        self.upload_measured_pvct()
        self.upload_measured_error()
        return FunctionResult.SUCCESS

    def upload_measured_pvct(self) -> FunctionResult:
        result = HardwareManager().fi_ace_get_pvct(ip=self.ip)

        if isinstance(result, Iterable):
            position, velocity, current, torque, timeout = result

            if timeout:
                self.flag_timeout = FlagState.SET
            else:
                self.flag_timeout = FlagState.CLEAR
                self.measured_position = position
                self.measured_velocity = velocity
                self.measured_current = current
                self.measured_effort = torque

        else:
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def upload_measured_error(self) -> FunctionResult:
        result = HardwareManager().fi_ace_get_error(ip=self.ip)

        if isinstance(result, Iterable):
            error, timeout = result

            if timeout:
                self.flag_timeout = FlagState.SET
            else:
                self.flag_timeout = FlagState.CLEAR
                self.measured_error_value = error

        else:
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download(self, **kwargs) -> FunctionResult:
        # target -> command
        self.target_to_command()

        # command -> output
        self.command_to_output()

        # download to actuator interface
        self.download_request()

        return FunctionResult.SUCCESS

    def target_to_command(self) -> FunctionResult:
        super().target_to_command()

        return FunctionResult.SUCCESS

    def command_to_output(self) -> FunctionResult:
        super().command_to_output()

        # from ActuatorMotor to ActuatorFIACE
        output_control_mode = \
            self.control_mode_mapping_from_unified_to_specified.get(
                self.command_control_mode, None
            )

        if output_control_mode:
            self.output_control_mode = output_control_mode

        return FunctionResult.SUCCESS

    def download_request(self) -> FunctionResult:
        # change control pid
        self.download_control_pid()

        # change control mode
        update_control_mode = None

        output_control_mode = self.output_control_mode
        download_control_mode = self.download_control_mode

        # control mode changed?
        if output_control_mode != download_control_mode:
            if output_control_mode in {
                ActuatorFIACEControlMode.CURRENT,
                ActuatorFIACEControlMode.EFFORT,
                ActuatorFIACEControlMode.VELOCITY,
                ActuatorFIACEControlMode.POSITION,
                ActuatorFIACEControlMode.PD,
            }:
                update_control_mode = output_control_mode
            else:
                # control mode not supported
                pass
        else:
            pass

        # only send control mode update when needed
        if update_control_mode is not None:
            Logger().print_info("ActuatorFIACE update control_modes = [")
            Logger().print_info(f"{self.ip} : {update_control_mode.name}", end="\n")
            Logger().print_info("]")

            # download control mode to actuator interface
            self.download_command_control_mode(update_control_mode)

        # execute specified mode control
        if output_control_mode == ActuatorFIACEControlMode.NONE:
            self.mode_of_operation = ActuatorModeOfOperation.NONE
            self.download_control_mode = ActuatorModeOfOperation.NONE

        elif output_control_mode == ActuatorFIACEControlMode.SERVO_ON:
            self.mode_of_operation = ActuatorModeOfOperation.NONE  # unified mode
            self.download_control_mode = ActuatorFIACEControlMode.SERVO_ON  # specified mode
            self.download_command_servo_on()

        elif output_control_mode == ActuatorFIACEControlMode.SERVO_OFF:
            self.mode_of_operation = ActuatorModeOfOperation.NONE  # unified mode
            self.download_control_mode = ActuatorFIACEControlMode.SERVO_OFF  # specified mode
            self.download_command_servo_off()

        elif output_control_mode == ActuatorFIACEControlMode.SET_PID:
            self.mode_of_operation = ActuatorModeOfOperation.NONE
            self.download_control_mode = ActuatorFIACEControlMode.SET_PID
            self.download_command_set_pid()

        elif (
                output_control_mode == ActuatorFIACEControlMode.SERVO_REBOOT or
                output_control_mode == ActuatorFIACEControlMode.SERVO_ZERO or
                output_control_mode == ActuatorFIACEControlMode.CLEAR_FAULT or
                output_control_mode == ActuatorFIACEControlMode.SET_PARAM or
                output_control_mode == ActuatorFIACEControlMode.SET_CONFIG or
                output_control_mode == ActuatorFIACEControlMode.ABSOLUTE_ZERO
        ):
            pass

        # --------------------------------------------------

        elif output_control_mode == ActuatorFIACEControlMode.VELOCITY:
            self.mode_of_operation = ActuatorModeOfOperation.VELOCITY  # unified mode
            self.download_control_mode = ActuatorFIACEControlMode.VELOCITY  # specified mode
            self.download_command_velocity_control()

        elif (
                output_control_mode == ActuatorFIACEControlMode.CURRENT or
                output_control_mode == ActuatorFIACEControlMode.EFFORT or
                output_control_mode == ActuatorFIACEControlMode.POSITION
        ):
            pass
        elif output_control_mode == ActuatorFIACEControlMode.PD:
            self.mode_of_operation = ActuatorModeOfOperation.PD  # unified mode
            self.download_control_mode = ActuatorFIACEControlMode.PD  # specified mode
            self.download_command_pd_control()

        # --------------------------------------------------

        else:
            self.mode_of_operation = ActuatorModeOfOperation.NONE
            self.download_control_mode = ActuatorModeOfOperation.NONE

        return FunctionResult.SUCCESS

    def download_control_pid(
            self,
            assign_control_mode=None,
            pass_repeat: bool = True,
            # pid values
            position_control_kp=None,
            velocity_control_kp=None,
            velocity_control_ki=None,
            effort_control_kp=None,
            effort_control_ki=None,
            # pd values
            pd_control_kp=None,
            pd_control_kd=None,
    ) -> FunctionResult:
        """
        Download control pid parameters

        Input:
        - assign_control_mode: default None
        - pass_repeat [bool]: whether check repeat value, and pass repeat value
        - position_control_kp [float]: position control kp
        - velocity_control_kp [float]: velocity control kp
        - velocity_control_ki [float]: velocity control ki
        - effort_control_kp [float]: effort control kp
        - effort_control_ki [float]: effort control ki
        - pd_control_kp [float]: pd control kp
        - pd_control_kd [float]: pd control kd

        Output:
        - function_result [FunctionResult]
        """
        # set target control pid
        self.set_target_control_pid(
            pd_control_kp=pd_control_kp,
            pd_control_kd=pd_control_kd,
            velocity_control_kp=velocity_control_kp,
            velocity_control_ki=velocity_control_ki,
        )

        if assign_control_mode is not None:
            download_control_pid_control_mode = assign_control_mode
        else:
            download_control_pid_control_mode = self.output_control_mode

        # download pid to hardware layer
        if download_control_pid_control_mode == ActuatorFIACEControlMode.NONE:
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == ActuatorFIACEControlMode.VELOCITY:
            result = self.download_velocity_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == ActuatorFIACEControlMode.PD:
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        else:
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        return result

    def download_pd_control_pid(self, pass_repeat=True) -> FunctionResult:
        # target -> variables
        if (
                pass_repeat is True
                and self.target_pd_control_kp == self.pd_control_kp
                and self.target_pd_control_kd == self.pd_control_kd
        ):
            # when the actuator has the same pid value, not send to the actuator hardware
            return FunctionResult.SUCCESS

        # target -> variables
        self.pd_control_kp = self.target_pd_control_kp
        self.pd_control_kd = self.target_pd_control_kd

        Logger().print_debug(
            f"Actuator {self.ip} download PD: "
            f"pd_kp={self.pd_control_kp} "
            f"pd_kd={self.pd_control_kd} "
        )

        result = HardwareManager().fi_ace_set_pd_param(
            ip=self.ip,
            pd_control_kp=self.pd_control_kp,
            pd_control_kd=self.pd_control_kd,
        )

        return result

    def download_velocity_control_pid(self, pass_repeat=True) -> FunctionResult:
        if (
                pass_repeat is True
                and self.target_velocity_control_kp == self.velocity_control_kp
                and self.target_velocity_control_ki == self.velocity_control_ki
        ):
            return FunctionResult.SUCCESS

        self.velocity_control_kp = self.target_velocity_control_kp
        self.velocity_control_ki = self.target_velocity_control_ki

        # skip sending if no gains specified — actuator keeps its stored defaults
        if self.velocity_control_kp is None and self.velocity_control_ki is None:
            return FunctionResult.SUCCESS

        Logger().print_debug(
            f"Actuator {self.ip} download VELOCITY pid: "
            f"v_kp={self.velocity_control_kp} "
            f"v_ki={self.velocity_control_ki} "
        )

        result = HardwareManager().fi_ace_set_velocity_param(
            ip=self.ip,
            velocity_control_kp=self.velocity_control_kp,
            velocity_control_ki=self.velocity_control_ki,
        )

        return result

    def download_command_control_mode(self, control_mode) -> FunctionResult:
        mode_of_operation = \
            self.mode_of_operation_mapping_from_control_mode.get(control_mode, None)

        if mode_of_operation is None:
            Logger().print_error(f"ActuatorFIACE {self.ip} control mode not supported")
            return FunctionResult.FAIL

        result = HardwareManager().fi_ace_set_control_mode(
            ip=self.ip, control_mode=mode_of_operation
        )

        return FunctionResult.SUCCESS if result == FunctionResult.SUCCESS else FunctionResult.FAIL

    def download_command_servo_on(self) -> FunctionResult:
        HardwareManager().fi_ace_set_servo_on(ip=self.ip)

        return FunctionResult.SUCCESS

    def download_command_servo_off(self) -> FunctionResult:
        HardwareManager().fi_ace_set_servo_off(ip=self.ip)

        return FunctionResult.SUCCESS

    def download_command_set_pid(self) -> FunctionResult:
        self.download_control_pid()

        return FunctionResult.SUCCESS

    def download_command_pd_control(self) -> FunctionResult:
        result = HardwareManager().fi_ace_set_pd_control(
            ip=self.ip,
            command_position=self.output_position,
            command_velocity=self.output_velocity,
        )

        if isinstance(result, Iterable):
            position, velocity, current, effort = result

            self.measured_position = position
            self.measured_velocity = velocity
            self.measured_current = current
            self.measured_effort = effort

        elif result == FunctionResult.SUCCESS:
            self.measured_position = self.measured_position
            self.measured_velocity = self.measured_velocity
            self.measured_current = self.measured_current
            self.measured_effort = self.measured_effort

        else:
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download_command_velocity_control(self) -> FunctionResult:
        result = HardwareManager().fi_ace_set_velocity_control(
            ip=self.ip,
            command_velocity=self.output_velocity,
        )

        if result != FunctionResult.SUCCESS:
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    # ----------------------------------------------------------------------------------------------------

    def get_error_code(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        self.error_code = self.measured_error_value

        return self.error_code

    # ----------------------------------------------------------------------------------------------------

    # Target Buffer
    def set_target_pd_control(self, position=0, velocity=0, effort=0) -> FunctionResult:
        self.target_control_mode = ActuatorFIACEControlMode.PD
        self.target_position = position
        self.target_velocity = velocity
        self.target_effort = effort
        return FunctionResult.SUCCESS

    # ----------------------------------------------------------------------------------------------------
