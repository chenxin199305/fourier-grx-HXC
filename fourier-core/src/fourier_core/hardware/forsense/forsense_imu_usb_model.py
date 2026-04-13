import threading


class IMUState:
    """
    一次完整的 IMU 数据帧
    """
    __slots__ = (
        "measured_quat",
        "measured_euler_angle",
        "measured_angular_velocity",
        "measured_linear_acceleration",
    )

    def __init__(self):
        self.measured_quat = [0.0, 0.0, 0.0, 1.0]
        self.measured_euler_angle = [0.0, 0.0, 0.0]
        self.measured_angular_velocity = [0.0, 0.0, 0.0]
        self.measured_linear_acceleration = [0.0, 0.0, 0.0]


class BaseIMU:
    """
    BaseIMU 抽象基类，提供统一接口
    """

    def update(self, quat=None, euler=None, gyro=None, accel=None):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def get_quat(self):
        raise NotImplementedError

    def get_euler(self):
        raise NotImplementedError

    def get_gyro(self):
        raise NotImplementedError

    def get_accel(self):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError


class NormalIMU(BaseIMU):
    """
    单缓冲 NormalIMU，兼容旧接口
    """

    def __init__(self, usb="/dev/ttyUSB0"):
        self.usb: str = usb

        # 控制标志
        self.flag_loss_connection: bool = False
        self.flag_subscribe: bool = False
        self.flag_thread_kill: bool = False
        self.comm_enable: bool = False

        # 状态数据
        self.measured_quat: list = [0.0, 0.0, 0.0, 1.0]
        self.measured_euler_angle: list = [0.0, 0.0, 0.0]
        self.measured_angular_velocity: list = [0.0, 0.0, 0.0]
        self.measured_linear_acceleration: list = [0.0, 0.0, 0.0]

    # ------------------------------------------------------------
    # 写线程：更新数据到 buffer（无锁）
    # ------------------------------------------------------------
    def update(self, quat=None, euler=None, gyro=None, accel=None):
        if quat is not None:
            self.measured_quat[:] = quat
        if euler is not None:
            self.measured_euler_angle[:] = euler
        if gyro is not None:
            self.measured_angular_velocity[:] = gyro
        if accel is not None:
            self.measured_linear_acceleration[:] = accel

    def publish(self):
        pass

    # ------------------------------------------------------------
    # 读线程：读取数据 （无锁）
    # ------------------------------------------------------------
    def get_quat(self):
        return self.measured_quat

    def get_euler(self):
        return self.measured_euler_angle

    def get_gyro(self):
        return self.measured_angular_velocity

    def get_accel(self):
        return self.measured_linear_acceleration

    def get_all(self):
        return (
            self.measured_quat,
            self.measured_euler_angle,
            self.measured_angular_velocity,
            self.measured_linear_acceleration,
        )


class DoubleBufferIMU(BaseIMU):
    """
    IMU 双缓冲结构：
    - back：写线程更新
    - front：读线程读取
    - publish：一次 swap，无锁一致性
    """

    def __init__(self, usb="/dev/ttyUSB0"):
        self.usb: str = usb

        # 控制标志
        self.flag_loss_connection = False
        self.flag_subscribe = False
        self.flag_thread_kill = False
        self.comm_enable = False

        # 状态数据
        self.front = IMUState()
        self.back = IMUState()

        # swap 需要轻量锁
        self.swap_lock = threading.Lock()

    # ----------------------------------------------------------------------
    # 写线程：更新 IMU 数据到 back buffer
    # ----------------------------------------------------------------------
    def update(self, quat=None, euler=None, gyro=None, accel=None):
        if quat is not None:
            self.back.measured_quat[:] = quat
        if euler is not None:
            self.back.measured_euler_angle[:] = euler
        if gyro is not None:
            self.back.measured_angular_velocity[:] = gyro
        if accel is not None:
            self.back.measured_linear_acceleration[:] = accel

    def publish(self):
        with self.swap_lock:
            self.front, self.back = self.back, self.front

    # ----------------------------------------------------------------------
    # 控制线程读取（无锁）
    # ----------------------------------------------------------------------
    def get_quat(self):
        f = self.front
        return f.measured_quat

    def get_euler(self):
        f = self.front
        return f.measured_euler_angle

    def get_gyro(self):
        f = self.front
        return f.measured_angular_velocity

    def get_accel(self):
        f = self.front
        return f.measured_linear_acceleration

    def get_all(self):
        f = self.front
        return (
            f.measured_quat,
            f.measured_euler_angle,
            f.measured_angular_velocity,
            f.measured_linear_acceleration,
        )


class IMUGroup:
    def __init__(self):
        self.imu_map: dict = {}

    def add_imu(self, usb, imu: BaseIMU):
        self.imu_map[usb] = imu


gl_imu_group = IMUGroup()
