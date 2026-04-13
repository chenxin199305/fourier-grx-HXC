from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.actuator.fi_actuator_motor import ActuatorMotor


class JointBase:
    def __init__(
            self,
            id: str = "joint_base",
            actuator: ActuatorMotor | None = None,
            direction=1,
            home_position=0.0,
            min_position=0.0,
            max_position=0.0,
            kinematic_reduction_ratio=1.0,
            kinetic_reduction_ratio=1.0,
            position_control_kp=None,
            velocity_control_kp=None,
            velocity_control_ki=None,
            pd_control_kp=None,
            pd_control_kd=None,
    ):

        self.id = id

        # Initialize actuator related attributes
        self._init_actuator(actuator=actuator)

        """
        Jason 2025-12-09:
        由于应用时，可能期望的参考坐标系和 Robot 定义的坐标系不一致，所以，针对 Application 又定义了相关的变量，存储应用层面的数据。
        """
        # application value
        self.application_direction: int = 1
        self.application_position: float = 0
        self.application_velocity: float = 0
        self.application_effort: float = 0
        self.application_offset_position: float = 0

        """
        Jason 2025-12-09:
        参考坐标系为 Robot 定义的坐标系
        """
        self.direction: int = direction
        self.home_position: float = home_position  # 零点位置
        self.min_position: float = min_position
        self.max_position: float = max_position
        self.kinematic_reduction_ratio: float = kinematic_reduction_ratio
        self.kinetic_reduction_ratio: float = kinetic_reduction_ratio

        self.position_control_kp: float | None = position_control_kp
        self.velocity_control_kp: float | None = velocity_control_kp
        self.velocity_control_ki: float | None = velocity_control_ki
        self.effort_control_kp: float | None = None
        self.effort_control_ki: float | None = None
        self.pd_control_kp: float | None = pd_control_kp
        self.pd_control_kd: float | None = pd_control_kd

        self.effort_transmission_ratio = 1

        self.radius = 0
        self.rate_speed = 0

        self.state = 0

        # target value
        # 1. target value is for change outside of the Joint class, not actually in the joint control loop
        # 2. target can be changed at any time, any place in the control system loop.
        self.target_control_mode = 0
        self.target_position: float = 0
        self.target_velocity: float = 0
        self.target_acceleration: float = 0
        self.target_effort: float = 0
        self.target_current: float = 0

        self.target_position_control_kp: float | None = position_control_kp
        self.target_velocity_control_kp: float | None = velocity_control_kp
        self.target_velocity_control_ki: float | None = velocity_control_ki
        self.target_effort_control_kp: float | None = None
        self.target_effort_control_ki: float | None = None
        self.target_pd_control_kp: float | None = pd_control_kp
        self.target_pd_control_kd: float | None = pd_control_kd

        # measured value
        # 1. measured value is the upload value from the actuator, not to be changed in the control loop
        self.measured_control_mode: JointControlMode = JointControlMode.NONE
        self.measured_position: float = 0
        self.measured_velocity: float = 0
        self.measured_acceleration: float = 0
        self.measured_effort: float = 0
        self.measured_current: float = 0

        # command value
        # 1. after go into the actuator control loop (control loop input),
        # command value is the "fixed target value", not to be changed in the control loop
        self.command_control_mode: JointControlMode = JointControlMode.NONE
        self.command_position: float = 0
        self.command_velocity: float = 0
        self.command_acceleration: float = 0
        self.command_effort: float = 0
        self.command_current: float = 0

        # output value
        # 1. output value is the output of the control loop
        self.output_control_mode: JointControlMode = JointControlMode.NONE
        self.output_position: float = 0
        self.output_velocity: float = 0
        self.output_acceleration: float = 0
        self.output_effort: float = 0
        self.output_current: float = 0

        self.output_min_position: float = 0
        self.output_min_velocity: float = 0
        self.output_min_acceleration: float = 0
        self.output_min_effort: float = 0

        self.output_max_position: float = 0
        self.output_max_velocity: float = 0
        self.output_max_acceleration: float = 0
        self.output_max_effort: float = 0

        self.protect_min_buffer_position: float = 0
        self.protect_min_prohibit_position: float = 0
        self.protect_min_velocity: float = 0
        self.protect_min_effort: float = 0
        self.protect_min_current: float = 0

        self.flag_protect_min_buffer_position: FlagState = FlagState.CLEAR
        self.flag_protect_min_prohibit_position: FlagState = FlagState.CLEAR
        self.flag_protect_min_velocity: FlagState = FlagState.CLEAR
        self.flag_protect_min_effort: FlagState = FlagState.CLEAR
        self.flag_protect_min_current: FlagState = FlagState.CLEAR

        self.protect_max_buffer_position: float = 0
        self.protect_max_prohibit_position: float = 0
        self.protect_max_velocity: float = 0
        self.protect_max_effort: float = 0
        self.protect_max_current: float = 0

        self.flag_protect_max_buffer_position: FlagState = FlagState.CLEAR
        self.flag_protect_max_prohibit_position: FlagState = FlagState.CLEAR
        self.flag_protect_max_velocity: FlagState = FlagState.CLEAR
        self.flag_protect_max_effort: FlagState = FlagState.CLEAR
        self.flag_protect_max_current: FlagState = FlagState.CLEAR

    def _init_actuator(self, actuator: ActuatorMotor | None) -> FunctionResult:
        if isinstance(actuator, ActuatorMotor):
            pass
        elif actuator is None:
            Logger().print_warning("JointBase actuator is None, set to default ActuatorMotor, may not work as expected")
        else:
            Logger().print_critical("JointBase actuator is not ActuatorMotor, JointBase class init failed")
            raise SystemExit(FunctionResult.FAIL)

        # if actuator is None, set to default ActuatorMotor
        self.actuator: ActuatorMotor | None = None

        if actuator is None:
            self.actuator = ActuatorMotor()
        else:
            self.actuator = actuator

        # actuator info
        self.actuator_state: int = 0
        self.actuator_control_mode: ActuatorControlMode = ActuatorControlMode.NONE
        self.actuator_measured_position: float = 0
        self.actuator_measured_velocity: float = 0
        self.actuator_measured_acceleration: float = 0
        self.actuator_measured_effort: float = 0
        self.actuator_measured_current: float = 0

        # control mode mapping
        self.control_mode_mapping_actuator_to_joint = {
            ActuatorControlMode.NONE: JointControlMode.NONE,
            ActuatorControlMode.CURRENT: JointControlMode.CURRENT,
            ActuatorControlMode.EFFORT: JointControlMode.EFFORT,
            ActuatorControlMode.VELOCITY: JointControlMode.VELOCITY,
            ActuatorControlMode.POSITION: JointControlMode.POSITION,
            ActuatorControlMode.TRAPEZOIDAL: JointControlMode.POSITION,
            ActuatorControlMode.PD: JointControlMode.PD,

            ActuatorControlMode.SERVO_ON: JointControlMode.OTHER,
            ActuatorControlMode.SERVO_OFF: JointControlMode.OTHER,
            ActuatorControlMode.SERVO_REBOOT: JointControlMode.OTHER,
            ActuatorControlMode.SERVO_ZERO: JointControlMode.OTHER,
            ActuatorControlMode.SET_HOME: JointControlMode.OTHER,
            ActuatorControlMode.FIND_HOME: JointControlMode.OTHER,
            ActuatorControlMode.CLEAR_FAULT: JointControlMode.OTHER,
            ActuatorControlMode.SET_PARAM: JointControlMode.OTHER,
            ActuatorControlMode.SET_CONFIG: JointControlMode.OTHER,
        }

        self.control_mode_mapping_joint_to_actuator = {
            JointControlMode.NONE: ActuatorControlMode.NONE,
            JointControlMode.CURRENT: ActuatorControlMode.CURRENT,
            JointControlMode.EFFORT: ActuatorControlMode.EFFORT,
            JointControlMode.VELOCITY: ActuatorControlMode.VELOCITY,
            JointControlMode.POSITION: ActuatorControlMode.POSITION,
            JointControlMode.PD: ActuatorControlMode.PD,

            JointControlMode.OTHER: None,
        }

        return FunctionResult.SUCCESS

    def upload(self) -> FunctionResult:
        """
        Upload 不仅更新数据，还要从底层获取数据
        """
        if self.actuator is None:
            return FunctionResult.FAIL
        else:
            self.actuator.upload()

        self.update()

        return FunctionResult.SUCCESS

    def update(self) -> FunctionResult:
        """
        Update 只更新数据，不会从底层读取数据
        """
        if self.actuator is None:
            Logger().print_warning("Joint update actuator is None")
            return FunctionResult.FAIL

        self.actuator_state: int = self.actuator.state
        self.actuator_control_mode: ActuatorControlMode = self.actuator.measured_control_mode
        self.actuator_measured_position: float = self.actuator.measured_position
        self.actuator_measured_velocity: float = self.actuator.measured_velocity
        self.actuator_measured_acceleration: float = self.actuator.measured_acceleration
        self.actuator_measured_effort: float = self.actuator.measured_effort
        self.actuator_measured_current: float = self.actuator.measured_current

        # state
        self.state = self.actuator_state

        # control mode
        self.measured_control_mode = \
            self.control_mode_mapping_actuator_to_joint.get(
                self.actuator_control_mode, JointControlMode.OTHER
            )

        # measured values
        if self.actuator_measured_position is not None:
            self.measured_position = (
                    self.actuator_measured_position / self.kinematic_reduction_ratio * self.direction
                    - self.home_position
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_position is None")

        if self.actuator_measured_velocity is not None:
            self.measured_velocity = (
                    self.actuator_measured_velocity / self.kinematic_reduction_ratio * self.direction
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_velocity is None")

        if self.actuator_measured_acceleration is not None:
            self.measured_acceleration = (
                    self.actuator_measured_acceleration / self.kinematic_reduction_ratio * self.direction
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_acceleration is None")

        if self.actuator_measured_effort is not None:
            self.measured_effort = (
                    self.actuator_measured_effort * self.kinetic_reduction_ratio * self.direction
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_effort is None")

        if self.actuator_measured_current is not None:
            self.measured_current = (self.actuator_measured_current * self.direction)
        else:
            Logger().print_error("Joint update actuator actuator_measured_current is None")

        # application values
        if self.measured_position is not None:
            self.application_position = (
                    self.measured_position * self.application_direction
                    + self.application_offset_position
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_position is None")

        if self.measured_velocity is not None:
            self.application_velocity = (
                self.measured_velocity
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_velocity is None")

        if self.measured_effort is not None:
            self.application_effort = (
                self.measured_effort
            )
        else:
            Logger().print_error("Joint update actuator actuator_measured_effort is None")

        # update flags
        self.flag_protect_min_buffer_position = FlagState.SET if self.measured_position < self.protect_min_buffer_position else FlagState.CLEAR
        self.flag_protect_max_buffer_position = FlagState.SET if self.measured_position > self.protect_max_buffer_position else FlagState.CLEAR
        self.flag_protect_min_prohibit_position = FlagState.SET if self.measured_position < self.protect_min_prohibit_position else FlagState.CLEAR
        self.flag_protect_max_prohibit_position = FlagState.SET if self.measured_position > self.protect_max_prohibit_position else FlagState.CLEAR
        self.flag_protect_min_velocity = FlagState.SET if self.measured_velocity < self.protect_min_velocity else FlagState.CLEAR
        self.flag_protect_max_velocity = FlagState.SET if self.measured_velocity > self.protect_max_velocity else FlagState.CLEAR
        self.flag_protect_min_effort = FlagState.SET if self.measured_effort < self.protect_min_effort else FlagState.CLEAR
        self.flag_protect_max_effort = FlagState.SET if self.measured_effort > self.protect_max_effort else FlagState.CLEAR
        self.flag_protect_min_current = FlagState.SET if self.measured_current < self.protect_min_current else FlagState.CLEAR
        self.flag_protect_max_current = FlagState.SET if self.measured_current > self.protect_max_current else FlagState.CLEAR

        return FunctionResult.SUCCESS

    def get_state(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.state

    def download(self) -> FunctionResult:
        """
        Download 不仅更新数据，还下发数据到执行器
        """
        # target -> command
        self.target_to_command()

        # command -> output
        self.command_to_output()

        # download to actuator interface
        self.flash_control_pid()
        self.flash_control_mode()
        self.flash_output_position()
        self.flash_output_velocity()
        self.flash_output_acceleration()
        self.flash_output_effort()

        # send data to actuator hardware
        self.actuator.download()

        return FunctionResult.SUCCESS

    def download_control_pid(
            self,
            assign_control_mode=None,
            pass_repeat=True
    ) -> FunctionResult:
        """
        Download control pid parameters

        Input:
        - assign_control_mode: default None
        - pass_repeat [bool]: whether check repeat value, and pass repeat value

        Output:
        - function_result [FunctionResult]
        """
        if assign_control_mode is not None:
            download_control_pid_control_mode = assign_control_mode
        else:
            download_control_pid_control_mode = self.output_control_mode

        # download pid to actuator layer
        if download_control_pid_control_mode == JointControlMode.NONE:
            """
            Jason 2025-12-20"
            从默认使用 PID Position 控制模式，修改为 PD 控制模式
            """
            # result = self.download_position_control_pid(pass_repeat=pass_repeat)
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == JointControlMode.CURRENT:
            result = self.download_current_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == JointControlMode.EFFORT:
            result = self.download_effort_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == JointControlMode.VELOCITY:
            result = self.download_velocity_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == JointControlMode.POSITION:
            result = self.download_position_control_pid(pass_repeat=pass_repeat)

        elif download_control_pid_control_mode == JointControlMode.PD:
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        else:
            """
            download_control_pid_control_mode doesn't match any control mode,
            set position control pid
            
            Jason 2025-12-20"
            从默认使用 PID Position 控制模式，修改为 PD 控制模式
            """
            # result = self.download_position_control_pid(pass_repeat=pass_repeat)
            result = self.download_pd_control_pid(pass_repeat=pass_repeat)

        return result

    def download_position_control_pid(self, pass_repeat=True) -> FunctionResult:
        """
        下载位置控制的PID
        """
        # update position control pid
        if (
                pass_repeat is True
                and self.target_position_control_kp == self.position_control_kp
                and self.target_velocity_control_kp == self.velocity_control_kp
                and self.target_velocity_control_ki == self.velocity_control_ki
        ):
            # when the joint has the same pid value, not send to the actuator
            return FunctionResult.SUCCESS

        # target -> variables
        self.position_control_kp = self.target_position_control_kp
        self.velocity_control_kp = self.target_velocity_control_kp
        self.velocity_control_ki = self.target_velocity_control_ki

        Logger().print_debug(
            f"Joint {self.id} download POSITION pid "
            f"p_kp={self.position_control_kp} "
            f"v_kp={self.velocity_control_kp} "
            f"v_ki={self.velocity_control_ki} "
        )

        # download pid to actuator hardware
        if self.actuator is not None:
            result = self.actuator.download_control_pid(
                assign_control_mode=ActuatorControlMode.POSITION,
                position_control_kp=self.position_control_kp,
                velocity_control_kp=self.velocity_control_kp,
                velocity_control_ki=self.velocity_control_ki,
                pass_repeat=pass_repeat,
            )

        else:
            Logger().print_warning("Joint flash_control_pd_pid actuator is None")
            return FunctionResult.FAIL

        return result

    def download_velocity_control_pid(self, pass_repeat=True) -> FunctionResult:
        """
        下载速度控制的PID
        """
        # update velocity control pid
        if (
                pass_repeat is True
                and self.target_velocity_control_kp == self.velocity_control_kp
                and self.target_velocity_control_ki == self.velocity_control_ki
        ):
            # when the joint has the same pid value, not send to the actuator
            return FunctionResult.SUCCESS

        # target -> variables
        self.velocity_control_kp = self.target_velocity_control_kp
        self.velocity_control_ki = self.target_velocity_control_ki

        Logger().print_debug(
            f"Joint {self.id} download VELOCITY pid "
            f"v_kp={self.velocity_control_kp} "
            f"v_ki={self.velocity_control_ki} "
        )

        # download pid to actuator hardware
        if self.actuator is not None:
            self.actuator.download_control_pid(
                assign_control_mode=ActuatorControlMode.VELOCITY,
                velocity_control_kp=self.velocity_control_kp,
                velocity_control_ki=self.velocity_control_ki,
                pass_repeat=pass_repeat,
            )

        else:
            Logger().print_warning("Joint flash_control_pd_pid actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download_effort_control_pid(self, pass_repeat=True) -> FunctionResult:
        """
        下载动能控制的PID
        """
        # update velocity control pid
        if (
                pass_repeat is True
                and self.target_effort_control_kp == self.effort_control_kp
                and self.target_effort_control_ki == self.effort_control_ki
        ):
            # when the joint has the same pid value, not send to the actuator
            return FunctionResult.SUCCESS

        # target -> variables
        self.effort_control_kp = self.target_effort_control_kp
        self.effort_control_ki = self.target_effort_control_ki

        Logger().print_debug(
            f"Joint {self.id} download EFFORT pid "
            f"c_kp={self.effort_control_kp} "
            f"c_ki={self.effort_control_ki} "
        )

        # download pid to actuator hardware
        if self.actuator is not None:
            self.actuator.download_control_pid(
                assign_control_mode=ActuatorControlMode.EFFORT,
                effort_control_kp=self.effort_control_kp,
                effort_control_ki=self.effort_control_ki,
                pass_repeat=pass_repeat,
            )

        else:
            Logger().print_warning("Joint flash_control_pd_pid actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def download_current_control_pid(self, pass_repeat=True) -> FunctionResult.SUCCESS:
        return self.download_effort_control_pid(pass_repeat=pass_repeat)

    def download_pd_control_pid(self, pass_repeat=True) -> FunctionResult:
        """
        下载PD控制的PID
        """
        # update velocity control pid
        if (
                pass_repeat is True
                and self.target_pd_control_kp == self.pd_control_kp
                and self.target_pd_control_kd == self.pd_control_kd
        ):
            # when the joint has the same pid value, not send to the actuator
            return FunctionResult.SUCCESS

        # target -> variables
        self.pd_control_kp = self.target_pd_control_kp
        self.pd_control_kd = self.target_pd_control_kd

        Logger().print_debug(
            f"Joint {self.id} download PD pid "
            f"pd_kp={self.pd_control_kp} "
            f"pd_kd={self.pd_control_kd} "
        )

        # download pid to actuator hardware
        if self.actuator is not None:
            self.actuator.download_control_pid(
                assign_control_mode=ActuatorControlMode.PD,
                pd_control_kp=self.pd_control_kp,
                pd_control_kd=self.pd_control_kd,
                pass_repeat=pass_repeat,
            )

        else:
            Logger().print_warning("Joint flash_control_pd_pid actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_control_pid(self) -> FunctionResult:
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_position_control_kp = None
        actuator_target_velocity_control_kp = None
        actuator_target_velocity_control_ki = None
        actuator_target_effort_control_kp = None
        actuator_target_effort_control_ki = None
        actuator_target_pd_control_kp = None
        actuator_target_pd_control_kd = None

        if (
                self.output_control_mode == JointControlMode.CURRENT or
                self.output_control_mode == JointControlMode.EFFORT
        ):
            if self.target_effort_control_kp:
                actuator_target_effort_control_kp = self.target_effort_control_kp

            if self.target_effort_control_ki:
                actuator_target_effort_control_ki = self.target_effort_control_ki

        elif self.output_control_mode == JointControlMode.VELOCITY:
            if self.target_velocity_control_kp:
                actuator_target_velocity_control_kp = self.target_velocity_control_kp

            if self.target_velocity_control_ki:
                actuator_target_velocity_control_ki = self.target_velocity_control_ki

        elif (
                self.output_control_mode == JointControlMode.POSITION
        ):
            if self.target_position_control_kp:
                actuator_target_position_control_kp = self.target_position_control_kp

            if self.target_velocity_control_kp:
                actuator_target_velocity_control_kp = self.target_velocity_control_kp

            if self.target_velocity_control_ki:
                actuator_target_velocity_control_ki = self.target_velocity_control_ki

        elif self.output_control_mode == JointControlMode.PD:
            if self.target_pd_control_kp:
                actuator_target_pd_control_kp = self.target_pd_control_kp

            if self.target_pd_control_kd:
                actuator_target_pd_control_kd = self.target_pd_control_kd

        else:
            pass

        if self.actuator is not None:
            self.actuator.set_target_control_pid(
                position_control_kp=actuator_target_position_control_kp,
                velocity_control_kp=actuator_target_velocity_control_kp,
                velocity_control_ki=actuator_target_velocity_control_ki,
                effort_control_kp=actuator_target_effort_control_kp,
                effort_control_ki=actuator_target_effort_control_ki,
                pd_control_kp=actuator_target_pd_control_kp,
                pd_control_kd=actuator_target_pd_control_kd,
            )
        else:
            Logger().print_warning("Joint flash_control_pid actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_control_mode(self) -> FunctionResult:
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_control_mode = \
            self.control_mode_mapping_joint_to_actuator.get(
                self.output_control_mode, None
            )

        # if joint control mode is not match actuator control mode, set to None and not send to the actuator
        if actuator_target_control_mode is None:
            return FunctionResult.SUCCESS

        if self.actuator is not None:
            self.actuator.set_target_control_mode(actuator_target_control_mode)
        else:
            Logger().print_warning("Joint flash_control_mode actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_output_position(self):
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_position = (
                (self.output_position + self.home_position)
                * self.kinematic_reduction_ratio * self.direction
        )

        if self.actuator is not None:
            self.actuator.set_target_position(actuator_target_position)
        else:
            Logger().print_warning("Joint flash_output_position actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_output_velocity(self):
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_velocity = self.output_velocity * self.kinematic_reduction_ratio * self.direction

        if self.actuator is not None:
            self.actuator.set_target_velocity(actuator_target_velocity)
        else:
            Logger().print_warning("Joint get_measured_velocity actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_output_acceleration(self):
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_acceleration = self.output_acceleration * self.kinematic_reduction_ratio * self.direction

        if self.actuator is not None:
            self.actuator.set_target_acceleration(actuator_target_acceleration)
        else:
            Logger().print_warning("Joint get_measured_acceleration actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_output_effort(self):
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_effort = self.output_effort / self.kinetic_reduction_ratio * self.direction

        if self.actuator is not None:
            self.actuator.set_target_effort(actuator_target_effort)
        else:
            Logger().print_warning("Joint get_measured_effort actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def flash_output_current(self):
        """
        Flash 操作只更新数据，并不会立即发送到硬件
        """

        actuator_target_current = self.output_current * self.direction

        if self.actuator is not None:
            self.actuator.set_target_current(actuator_target_current)
        else:
            Logger().print_warning("Joint get_measured_current actuator is None")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def target_to_command(self):
        self.command_control_mode = self.target_control_mode
        self.command_position = self.target_position
        self.command_velocity = self.target_velocity
        self.command_acceleration = self.target_acceleration
        self.command_effort = self.target_effort
        self.command_current = self.target_current

    def command_to_output(self):
        self.output_control_mode = self.command_control_mode
        self.output_position = self.command_position
        self.output_velocity = self.command_velocity
        self.output_acceleration = self.command_acceleration
        self.output_effort = self.command_effort
        self.output_current = self.command_current

    def set_home_position(self, home_position, consider_reduction=True) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        if consider_reduction:
            self.home_position = home_position * self.kinematic_reduction_ratio * self.direction
        else:
            self.home_position = home_position

        return FunctionResult.SUCCESS

    def set_application_direction(self, direction) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.application_direction = direction
        return FunctionResult.SUCCESS

    def set_application_offset_position(self, offset_position) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.application_offset_position = offset_position
        return FunctionResult.SUCCESS

    def set_target_control_mode(self, control_mode) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        if control_mode == JointControlMode.POSITION_PSEUDO_PD:
            control_mode = JointControlMode.POSITION

        self.target_control_mode = control_mode
        return FunctionResult.SUCCESS

    def set_target_position(self, position) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_position = position
        return FunctionResult.SUCCESS

    def set_target_velocity(self, velocity) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_velocity = velocity
        return FunctionResult.SUCCESS

    def set_target_acceleration(self, acceleration) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_acceleration = acceleration
        return FunctionResult.SUCCESS

    def set_target_effort(self, effort) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_effort = effort
        return FunctionResult.SUCCESS

    def set_target_current(self, current) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_current = current
        return FunctionResult.SUCCESS

    def set_target_position_control_kp(self, kp) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_position_control_kp = kp
        return FunctionResult.SUCCESS

    def set_target_velocity_control_kp(self, kp):
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_velocity_control_kp = kp
        return FunctionResult.SUCCESS

    def set_target_velocity_control_ki(self, ki) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_velocity_control_ki = ki
        return FunctionResult.SUCCESS

    def set_target_effort_control_kp(self, kp) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_effort_control_kp = kp
        return FunctionResult.SUCCESS

    def set_target_effort_control_ki(self, ki) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_effort_control_ki = ki
        return FunctionResult.SUCCESS

    def set_target_pd_control_kp(self, kp) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_pd_control_kp = kp
        return FunctionResult.SUCCESS

    def set_target_pd_control_kd(self, kd) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_pd_control_kd = kd
        return FunctionResult.SUCCESS

    def set_target_position_control(self, position=None, velocity=None, acceleration=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.set_target_control_mode(JointControlMode.POSITION)

        if position:
            self.set_target_position(position)

        if velocity:
            self.set_target_velocity(velocity)

        if acceleration:
            self.set_target_acceleration(acceleration)

        return FunctionResult.SUCCESS

    def set_target_velocity_control(self, velocity=None, acceleration=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.set_target_control_mode(JointControlMode.VELOCITY)

        if velocity:
            self.set_target_velocity(velocity)

        if acceleration:
            self.set_target_acceleration(acceleration)

        return FunctionResult.SUCCESS

    def set_target_effort_control(self, effort=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.set_target_control_mode(JointControlMode.EFFORT)

        if effort:
            self.set_target_effort(effort)

        return FunctionResult.SUCCESS

    def set_target_current_control(self, current=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.set_target_control_mode(JointControlMode.CURRENT)

        if current:
            self.set_target_current(current)

        return FunctionResult.SUCCESS

    def set_target_pd_control(self, position=None, velocity=None, effort=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.set_target_control_mode(JointControlMode.PD)

        if position:
            self.set_target_position(position)

        if velocity:
            self.set_target_velocity(velocity)

        if effort:
            self.set_target_effort(effort)

        return FunctionResult.SUCCESS

    # ------------------- Set -------------------

    def calculate_position_pseudo_pd_kp_kd(self, kp, kd):
        """
        Calculate position pseudo pd kp kd
        """
        pseudo_kp, pseudo_kd = self.actuator.calculate_position_pseudo_pd_kp_kd(kp, kd)

        return pseudo_kp, pseudo_kd
