import socket
import threading
import msgpack

from fourier_core.predefine import *
from fourier_core.logger import *

from fourier_grx.comm import *


class SyncClientSocket:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(SyncClientSocket, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            server_host=None,
            server_port=None,
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

        # 动态链接数据模型
        self._dynalink_manager = DynalinkManager()

        # -----------------------------
        # 服务端信息
        # -----------------------------
        # Server 地址（自动发现）
        self.server_host = server_host
        self.server_port = server_port

        # UDP 属性
        self.max_packet_size = max_packet_size

        # -----------------------------
        # UDP Socket 初始化
        # -----------------------------
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 可选：允许绑定同一个端口（多客户端场景）
        self._socket.bind(("0.0.0.0", 0))  # 绑定本地随机端口

        # -----------------------------
        # 后台接收线程
        # -----------------------------
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

        # -----------------------------
        # 后台线程发现 Server
        # -----------------------------
        self.broadcast_port = broadcast_port
        self.broadcast_interval = broadcast_interval

        if auto_discover:
            self._discovery_thread = threading.Thread(target=self._discover_server_loop, daemon=True)
            self._discovery_thread.start()

        Logger().print_debug("#################################")
        Logger().print_debug(
            f"{self.__class__.__name__} Socket Config \n"
            f" Server Host: {self.server_host}\n"
            f" Server Port: {self.server_port}\n"
            f" Max Packet Size: {self.max_packet_size}\n"
            f" Auto Discover: {auto_discover}\n"
            f" Broadcast Port: {self.broadcast_port}\n"
            f" Broadcast Interval: {self.broadcast_interval}\n"
        )
        Logger().print_debug("#################################")

    # --------------------------------------------------
    # 单例析构
    # --------------------------------------------------
    def __del__(self):
        self.close()

    # --------------------------------------------------
    # 自动发现服务器
    # --------------------------------------------------
    def _discover_server_loop(self):
        """
        后台线程监听 UDP 广播，自动发现 Server。
        """
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind(("0.0.0.0", self.broadcast_port))
        broadcast_socket.settimeout(self.broadcast_interval)

        while self.server_host is None:
            try:
                data, addr = broadcast_socket.recvfrom(1024)
                server_info = msgpack.unpackb(data)
                self.server_host = server_info["host"]
                self.server_port = server_info["port"]
            except socket.timeout:
                continue
            except Exception:
                continue

        broadcast_socket.close()

    def server_discovered(self) -> bool:
        """
        检查是否已发现 Server。
        """
        return self.server_host is not None and self.server_port is not None

    # --------------------------------------------------
    # recv loop（后台线程）
    # --------------------------------------------------
    def _recv_loop(self):
        """
        后台线程循环接收 Server 数据包。
        """
        while True:
            try:
                body, addr = self._socket.recvfrom(self.max_packet_size)
                packet = msgpack.unpackb(body)
                self._subscribe_handler(packet)
            except Exception:
                continue

    # --------------------------------------------------
    # publish（Client → Server）
    # --------------------------------------------------
    def publish(self, key=None, value=None) -> FunctionResult:
        """
        同步发布数据到 Server。
        """
        if self.verbose:
            print(f"{self.__class__.__name__} publishing key={key} value={value}")

        if key is not None and value is not None:
            packet = msgpack.packb({"key": key, "data": value})
            self._publish_handler(packet)
        else:
            for k in self.topic_keys:
                data_dict = getattr(self._dynalink_manager, f"dynalink_{k}").write_to_dict()
                packet = msgpack.packb({"key": k, "data": data_dict})
                self._publish_handler(packet)

        return FunctionResult.SUCCESS

    def _publish_handler(self, packet: bytes):
        if not self.server_discovered():
            return

        try:
            self._socket.sendto(packet, (self.server_host, self.server_port))
        except Exception:
            pass

    # --------------------------------------------------
    # subscribe（Server → Client）
    # --------------------------------------------------
    def _subscribe_handler(self, packet):
        key = packet.get("key")
        data = packet.get("data")

        if self.verbose:
            print(f"{self.__class__.__name__} subscribing key={key} data={data}")

        if key in self.topic_keys:
            getattr(self._dynalink_manager, f"dynalink_{key}").read_from_dict(data)

    # --------------------------------------------------
    # close
    # --------------------------------------------------
    def close(self):
        try:
            if getattr(self, "_socket", None):
                self._socket.close()
        except Exception:
            pass
