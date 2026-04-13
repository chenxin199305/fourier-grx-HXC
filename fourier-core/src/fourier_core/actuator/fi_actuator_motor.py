from fourier_core.predefine import *
from fourier_core.actuator.fi_actuator_base import ActuatorBase

"""
Design Idea:
1. ActuatorMotor 作为父类，提供通用的变量属性，这个方便更上层的调用。
2. ActuatorXXX(ActuatorMotor) 作为子类，可以有自己的一些特性的内容，如：
   - 使用 CAN 通信的，可以有 CANOpenTable
   - 使用 Ethernet Json 通信的，可以有 JasonTable
   其他类似。
"""


class ActuatorMotor(ActuatorBase):
    def __init__(
            self,
            id: str = "",
            manufactor: ActuatorManufactor = ActuatorManufactor.NONE,
            type=None
    ):
        super().__init__(id=id)

        self.manufactor: ActuatorManufactor = manufactor
        self.type = type

        self.accessible: int = 0
        self.state: int = 0
        self.error_code: int = 0

        self.mode_of_operation: int = 0  # 这个是给上层获取信息的上层接口
        self.download_control_mode: int = 0  # 这个是为了适配不同厂商的参数设计的底层接口

        self.flag_calibration: FlagState = FlagState.CLEAR
        self.flag_enable: FlagState = FlagState.CLEAR
        self.flag_timeout: FlagState = FlagState.CLEAR
        self.flag_encoder: FlagState = FlagState.CLEAR
        self.flag_encoder_ready: FlagState = FlagState.CLEAR

        self.position_control_kp: float | None = None  # None: use actuator default value
        self.velocity_control_kp: float | None = None  # None: use actuator default value
        self.velocity_control_ki: float | None = None  # None: use actuator default value
        self.effort_control_kp: float | None = None  # None: use actuator default value
        self.effort_control_ki: float | None = None  # None: use actuator default value
        self.pd_control_kp: float | None = None  # None: use actuator default value
        self.pd_control_kd: float | None = None  # None: use actuator default value

        # target value
        # 1. target value is for change outside of the acutator,
        # not actually in the actuator control loop
        self.target_control_mode: ActuatorControlMode = ActuatorControlMode.NONE
        self.target_position: float = 0
        self.target_velocity: float = 0
        self.target_acceleration: float = 0
        self.target_effort: float = 0
        self.target_current: float = 0
        self.target_position_control_kp: float | None = None  # None: use actuator default value
        self.target_velocity_control_kp: float | None = None  # None: use actuator default value
        self.target_velocity_control_ki: float | None = None  # None: use actuator default value
        self.target_effort_control_kp: float | None = None  # None: use actuator default value
        self.target_effort_control_ki: float | None = None  # None: use actuator default value
        self.target_pd_control_kp: float | None = None  # None: use actuator default value
        self.target_pd_control_kd: float | None = None  # None: use actuator default value

        self.measured_control_mode: ActuatorControlMode = ActuatorControlMode.NONE
        self.measured_position: float = 0
        self.measured_velocity: float = 0
        self.measured_acceleration: float = 0
        self.measured_effort: float = 0
        self.measured_current: float = 0

        self.measured_error_value: int = 0

        # command value
        # 1. after go into the actuator control loop (control loop input),
        # command value is the "fixed target value", not to be changed in the control loop
        self.command_control_mode: ActuatorControlMode = ActuatorControlMode.NONE
        self.command_position: float = 0
        self.command_velocity: float = 0
        self.command_acceleration: float = 0
        self.command_effort: float = 0
        self.command_current: float = 0

        # output value
        # 1. output value is the output of the control loop
        self.output_control_mode: ActuatorControlMode = ActuatorControlMode.NONE
        self.output_position: float = 0
        self.output_velocity: float = 0
        self.output_acceleration: float = 0
        self.output_effort: float = 0
        self.output_current: float = 0

        # accessible check
        self.accessible_check_count = 0
        self.flag_accessible = FlagState.SET

    def init(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def comm(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def check(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    def subscribe(self, **kwargs) -> FunctionResult:
        return FunctionResult.SUCCESS

    # ------------------- Upload -------------------

    def upload(self, **kwargs) -> FunctionResult:
        """
        Upload 不仅更新数据，还要从底层获取数据
        """

        return FunctionResult.SUCCESS

    # ------------------- Upload -------------------

    # ------------------- Download -------------------

    def download(self, **kwargs) -> FunctionResult:
        """
        Download 不仅更新数据，还下发数据到执行器
        """

        # target -> command
        self.target_to_command()

        # command -> output
        self.command_to_output()

        # download to actuator interface
        self.download_request()

        return FunctionResult.SUCCESS

    def download_control_pid(
            self,
            assign_control_mode=None,
            pass_repeat=True,
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
        # set control pid
        self.set_target_control_pid(
            position_control_kp,
            velocity_control_kp,
            velocity_control_ki,
            effort_control_kp,
            effort_control_ki,
            pd_control_kp,
            pd_control_kd,
        )

        # download to actuator interface
        # ...

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

    def download_request(self):
        return FunctionResult.SUCCESS

    # ------------------- Download -------------------

    # ------------------- Get -------------------

    def get_accessible(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.accessible

    def get_state(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.state

    def get_error_code(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.error_code

    def get_mode_of_operation(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.mode_of_operation

    def get_target_control_mode(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_control_mode

    def get_target_position(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_position

    def get_target_velocity(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_velocity

    def get_target_acceleration(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_acceleration

    def get_target_effort(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_effort

    def get_target_current(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.target_current

    def get_command_control_mode(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_control_mode

    def get_command_position(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_position

    def get_command_velocity(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_velocity

    def get_command_acceleration(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_acceleration

    def get_command_effort(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_effort

    def get_command_current(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.command_current

    def get_output_control_mode(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_control_mode

    def get_output_position(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_position

    def get_output_velocity(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_velocity

    def get_output_acceleration(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_acceleration

    def get_output_effort(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_effort

    def get_output_current(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.output_current

    def get_measured_control_mode(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.measured_control_mode

    def get_flag_enable(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.flag_enable

    def get_flag_timeout(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.flag_timeout

    def get_flag_encoder(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.flag_encoder

    def get_flag_encoder_ready(self):
        """
        Get 获取的是缓存的状态，不是实时的状态
        """
        return self.flag_encoder_ready

    # ------------------- Get -------------------

    # ------------------- Set -------------------

    def set_servo_on(self) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        return FunctionResult.SUCCESS

    def set_servo_off(self) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        return FunctionResult.SUCCESS

    def set_target_control_pid(
            self,
            position_control_kp=None,
            velocity_control_kp=None,
            velocity_control_ki=None,
            effort_control_kp=None,
            effort_control_ki=None,
            pd_control_kp=None,
            pd_control_kd=None,
    ) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态

        Input: \n
        - position_control_kp [float]: 位置控制的比例系数
        - velocity_control_kp [float]: 速度控制的比例系数
        - velocity_control_ki [float]: 速度控制的积分系数
        - effort_control_kp [float]: 力矩控制的比例系数
        - effort_control_ki [float]: 力矩控制的积分系数
        - pd_control_kp [float]: PD 控制的比例系数
        - pd_control_kd [float]: PD 控制的微分系数

        Output: \n
        - FunctionResult: 设置结果

        Note: \n
        - 如果 Input 为 None，则使用原来的值
        """
        if position_control_kp is not None:
            self.target_position_control_kp = position_control_kp

        if velocity_control_kp is not None:
            self.target_velocity_control_kp = velocity_control_kp

        if velocity_control_ki is not None:
            self.target_velocity_control_ki = velocity_control_ki

        if effort_control_kp is not None:
            self.target_effort_control_kp = effort_control_kp

        if effort_control_ki is not None:
            self.target_effort_control_ki = effort_control_ki

        if pd_control_kp is not None:
            self.target_pd_control_kp = pd_control_kp

        if pd_control_kd is not None:
            self.target_pd_control_kd = pd_control_kd

        return FunctionResult.SUCCESS

    def set_target_control_mode(self, control_mode: ActuatorControlMode) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
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

    def set_target_position_control(self, position, velocity=None, acceleration=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_control_mode = ActuatorControlMode.POSITION
        self.target_position = position

        if velocity is not None:
            self.target_velocity = velocity

        if acceleration is not None:
            self.target_acceleration = acceleration

        return FunctionResult.SUCCESS

    def set_target_velocity_control(self, velocity, acceleration=None) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_control_mode = ActuatorControlMode.VELOCITY
        self.target_velocity = velocity

        if acceleration is not None:
            self.target_acceleration = acceleration

        return FunctionResult.SUCCESS

    def set_target_effort_control(self, effort) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_control_mode = ActuatorControlMode.EFFORT
        self.target_effort = effort
        return FunctionResult.SUCCESS

    def set_target_pd_control(self, position=0, velocity=0, effort=0) -> FunctionResult:
        """
        Set 设置的是缓存的状态，不是实时修改的状态
        """
        self.target_control_mode = ActuatorControlMode.PD
        self.target_position = position
        self.target_velocity = velocity
        self.target_effort = effort
        return FunctionResult.SUCCESS

    # ------------------- Set -------------------

    # ------------------- Absolute Encoder -------------------

    def upload_absolute_position(self) -> FunctionResult:
        """
        上传绝对编码器位置
        """
        return FunctionResult.SUCCESS

    def download_absolute_zero(self) -> FunctionResult:
        """
        校准绝对编码器零点
        """
        return FunctionResult.SUCCESS

    # ------------------- Absolute Encoder -------------------

    def calculate_position_pseudo_pd_kp_kd(self, kp, kd):
        """
        Calculate the position pseudo PD control kp and kd
        """
        # calculate the position pseudo PD control kp and kd
        pseudo_kp, pseudo_kd = kp, kd

        return pseudo_kp, pseudo_kd
