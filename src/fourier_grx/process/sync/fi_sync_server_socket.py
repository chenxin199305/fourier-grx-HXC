import time
import socket
import threading
import msgpack

from fourier_core.predefine import *
from fourier_core.logger import *

from fourier_grx.comm import *


class SyncServerSocket:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SyncServerSocket, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            host="0.0.0.0",
            port=5566,
            max_packet_size=65507,
            # 自动发现服务
            auto_discover: bool = True,
            broadcast_port=9527,  # 周星驰：编号9527，广播端口
            broadcast_interval=1.0,
            # 调试输出
            verbose: bool = False,
    ):
        # 避免单例重复初始化
        if self._initialized:
            return
        self._initialized = True

        # 设置日志输出开关
        self.verbose = verbose

        # 主题键列表
        self.topic_keys = ["comm", "core", "robot", "task", "grx", "rehab"]

        # 初始化通信数据模型
        self._dynalink_manager = DynalinkManager()

        # 基本配置
        self.host = host
        self.port = port
        self.max_packet_size = max_packet_size

        # -----------------------------
        # UDP Socket 初始化
        # -----------------------------
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))

        # 记录所有需要广播的客户端地址
        self._client_addrs = set()

        # -----------------------------
        # 后台接收线程
        # -----------------------------
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

        # -----------------------------
        # 后台线程发现 Client 并广播 Server 信息
        # -----------------------------
        self.broadcast_port = broadcast_port
        self.broadcast_interval = broadcast_interval

        if auto_discover:
            self._broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
            self._broadcast_thread.start()

        Logger().print_debug("#################################")
        Logger().print_debug(
            f"{self.__class__.__name__} Socket Config \n"
            f" Host: {self.host}\n"
            f" Port: {self.port}\n"
            f" Max Packet Size: {self.max_packet_size}\n"
            f" Auto Discover: {auto_discover}\n"
            f" Broadcast Port: {self.broadcast_port}\n"
            f" Broadcast Interval: {self.broadcast_interval}\n"
        )
        Logger().print_debug("#################################")

    # --------------------------------------------------
    # 单例析构：关闭 socket
    # --------------------------------------------------
    def __del__(self):
        self.close()

    # -----------------------------
    # 广播线程（自动发现服务器信息）
    # -----------------------------
    def _broadcast_loop(self):
        """
        周期性在局域网广播 Server 的 IP 和端口
        """
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            try:
                # 获取本机 IP（可用第一个非环回地址）
                server_ip = self.host if self.host != "0.0.0.0" else socket.gethostbyname(socket.gethostname())
                info = msgpack.packb({"host": server_ip, "port": self.port})
                broadcast_socket.sendto(info, ("255.255.255.255", self.broadcast_port))
                time.sleep(self.broadcast_interval)
            except Exception:
                continue

    # --------------------------------------------------
    # 接受数据（后台线程）
    # --------------------------------------------------
    def _recv_loop(self):
        """
        后台线程循环接收 Client 数据包。
        """
        while True:
            try:
                body, addr = self._server_socket.recvfrom(self.max_packet_size)
                self._client_addrs.add(addr)

                packet = msgpack.unpackb(body)
                self._subscribe_handler(packet)

            except Exception as e:
                Logger().print_debug(f"{self.__class__.__name__} recv loop error: {e}")
                continue

    # --------------------------------------------------
    # 服务器->客户端 发布数据
    # --------------------------------------------------
    def publish(self, key=None, value=None) -> FunctionResult:
        """
        服务器向所有已知客户端发布数据。
        """
        if self.verbose:
            print(f"{self.__class__.__name__} publishing key={key} value={value}")

        if key is not None and value is not None:
            packet = msgpack.packb({"key": key, "data": value})
            self._publish_handler(packet)
        else:
            for key in self.topic_keys:
                data_dict = getattr(self._dynalink_manager, f"dynalink_{key}").read_to_dict()
                packet = msgpack.packb({"key": key, "data": data_dict})
                self._publish_handler(packet)

        return FunctionResult.SUCCESS

    def _publish_handler(self, packet):
        dead_addrs = []

        for addr in list(self._client_addrs):
            try:
                self._server_socket.sendto(packet, addr)
            except Exception:
                dead_addrs.append(addr)

        # 清理已断开客户端
        for addr in dead_addrs:
            if addr in self._client_addrs:
                self._client_addrs.remove(addr)

    # --------------------------------------------------
    # 客户端->服务器 接收数据
    # --------------------------------------------------
    def _subscribe_handler(self, packet):
        key = packet.get("key")
        data = packet.get("data")

        if self.verbose:
            print(f"{self.__class__.__name__} subscribing key={key} data={data}")

        if key in self.topic_keys:
            getattr(self._dynalink_manager, f"dynalink_{key}").write_from_dict(data)

    # --------------------------------------------------
    # 关闭连接
    # --------------------------------------------------
    def close(self):
        try:
            if getattr(self, "_server_socket", None):
                self._server_socket.close()
        except Exception:
            pass
