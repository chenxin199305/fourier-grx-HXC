import threading


class ACEState:
    """
    存储一次完整的 PVC(T) 状态
    """
    __slots__ = (
        "measured_position",
        "measured_velocity",
        "measured_current",
        "measured_torque",
        "status_word",
        "error_code",
        "timeout",
    )

    def __init__(self):
        self.measured_position: float = 0.0
        self.measured_velocity: float = 0.0
        self.measured_current: float = 0.0
        self.measured_torque: float = 0.0
        self.status_word: int = 0
        self.error_code: int = 0
        self.timeout: int = 0


class BaseACE:
    """
    ACE 基类，提供统一接口
    """

    # -----------------------------
    # 写线程接口
    # -----------------------------
    def update(self, p=None, v=None, c=None, t=None, s=None, e=None, o=None):
        raise NotImplementedError

    def publish(self):
        pass

    # -----------------------------
    # 读线程接口
    # -----------------------------
    def get_pvc(self):
        raise NotImplementedError

    def get_pvct(self):
        raise NotImplementedError

    def get_status_word(self):
        raise NotImplementedError

    def get_error_code(self):
        raise NotImplementedError

    def get_timeout(self):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError


class NormalACE(BaseACE):
    """
    Fourier Smart Actuator 的数据模型
    该类用于存储 NormalACE 的状态和命令数据
    (常规实现版版本）
    """

    def __init__(self, server_ip="192.168.137.100"):
        self.server_ip: str = server_ip

        # 控制标志
        self.flag_loss_connection: bool = False
        self.flag_subscribe: bool = False
        self.comm_enable: bool = False

        # 状态数据
        self.measured_position: float = 0
        self.measured_velocity: float = 0
        self.measured_torque: float = 0
        self.measured_current: float = 0
        self.status_word: int = 0
        self.error_code: int = 0
        self.timeout: int = 0

        # 指令数据 (暂未使用上)
        # self.command_mode_of_operation: int = 0
        # self.command_position: float = 0
        # self.command_velocity: float = 0
        # self.command_torque: float = 0
        # self.command_current: float = 0

    # ------------------------------------------------------------
    # 写线程：更新数据到 buffer（无锁）
    # ------------------------------------------------------------
    def update(self, p=None, v=None, c=None, t=None, s=None, e=None, o=None):
        """
        更新数据到 buffer（无锁）

        :param p: 位置
        :param v: 速度
        :param c: 电流
        :param t: 力矩
        :param s: 状态字
        :param e: 错误码
        :param o: 超时
        """
        if p is not None:
            self.measured_position = p
        if v is not None:
            self.measured_velocity = v
        if c is not None:
            self.measured_current = c
        if t is not None:
            self.measured_torque = t
        if s is not None:
            self.status_word = s
        if e is not None:
            self.error_code = e
        if o is not None:
            self.timeout = o

    def publish(self):
        pass

    # ------------------------------------------------------------
    # 读线程：读取数据 （无锁）
    # ------------------------------------------------------------
    def get_pvc(self):
        return (
            self.measured_position,
            self.measured_velocity,
            self.measured_current,
        )

    def get_pvct(self):
        return (
            self.measured_position,
            self.measured_velocity,
            self.measured_current,
            self.measured_torque,
        )

    def get_status_word(self):
        return self.status_word

    def get_error_code(self):
        return self.error_code

    def get_timeout(self):
        return self.timeout

    def get_all(self):
        return (
            self.measured_position,
            self.measured_velocity,
            self.measured_current,
            self.measured_torque,
            self.status_word,
            self.error_code,
            self.timeout,
        )


class DoubleBufferACE(BaseACE):
    """
    Fourier Smart Actuator 的数据模型
    (无锁双缓冲版本)
    - back_buffer：写线程更新
    - front_buffer：读线程读取
    - publish()：原子交换 front/back
    """

    def __init__(self, server_ip="192.168.137.100"):
        self.server_ip = server_ip

        # 控制标志
        self.flag_loss_connection = False
        self.flag_subscribe = False
        self.comm_enable = False

        # 状态数据双缓冲
        self.front = ACEState()
        self.back = ACEState()

        # 使用递归锁来确保更新操作的线程安全
        self.update_lock = threading.RLock()
        self.swap_lock = threading.Lock()

    # ------------------------------------------------------------
    # 写线程：更新数据到 back buffer（加锁）
    # ------------------------------------------------------------
    def update(self, p=None, v=None, c=None, t=None, s=None, e=None, o=None):
        with self.update_lock:  # 使用 RLock 进行锁定，保证线程安全
            if p is not None:
                self.back.measured_position = p
            if v is not None:
                self.back.measured_velocity = v
            if c is not None:
                self.back.measured_current = c
            if t is not None:
                self.back.measured_torque = t
            if s is not None:
                self.back.status_word = s
            if e is not None:
                self.back.error_code = e
            if o is not None:
                self.back.timeout = o

    def publish(self):
        with self.swap_lock:
            self.front, self.back = self.back, self.front

    # ------------------------------------------------------------
    # 读线程：读取数据（无锁）
    # ------------------------------------------------------------
    def get_pvc(self):
        f = self.front
        return (
            f.measured_position,
            f.measured_velocity,
            f.measured_current,
        )

    def get_pvct(self):
        f = self.front
        return (
            f.measured_position,
            f.measured_velocity,
            f.measured_current,
            f.measured_torque,
        )

    def get_status_word(self):
        f = self.front
        return f.status_word

    def get_error_code(self):
        f = self.front
        return f.error_code

    def get_timeout(self):
        f = self.front
        return f.timeout

    def get_all(self):
        f = self.front
        return (
            f.measured_position,
            f.measured_velocity,
            f.measured_current,
            f.measured_torque,
            f.status_word,
            f.error_code,
            f.timeout,
        )


class ACEGroup:
    def __init__(self):
        self.ace_map: dict = {}

    def add_ace(self, server_ip, ace: BaseACE):
        self.ace_map[server_ip] = ace


gl_ace_model_group = ACEGroup()
