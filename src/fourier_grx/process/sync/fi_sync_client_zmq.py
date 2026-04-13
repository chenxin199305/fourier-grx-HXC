import time
import threading
import zmq
import msgpack
import numpy
import socket

from fourier_core.predefine import *
from fourier_core.logger import *

from fourier_grx.comm import *


class SyncClientZMQ:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(SyncClientZMQ, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            server_host=None,
            server_pub_port=None,
            server_sub_port=None,
            # 自动发现服务
            auto_discover: bool = True,
            broadcast_port=9527,
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
        self.server_host = server_host
        self.pub_port = server_sub_port
        self.sub_port = server_pub_port

        # ZeroMQ context
        self._context = zmq.Context()

        # PUB socket: client -> server
        self._pub_socket = self._context.socket(zmq.PUB)

        # SUB socket: server -> client
        self._sub_socket = self._context.socket(zmq.SUB)

        # 订阅所有主题
        for key in self.topic_keys:
            self._sub_socket.setsockopt_string(zmq.SUBSCRIBE, key)

        # -----------------------------
        # 后台接收线程
        # -----------------------------
        self._sub_thread = threading.Thread(target=self._sub_loop, daemon=True)
        self._sub_thread.start()

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
            f"{self.__class__.__name__} ZMQ Config \n"
            f"PUB socket: tcp://{self.server_host}:{self.pub_port} \n"
            f"SUB socket: tcp://{self.server_host}:{self.sub_port} \n"
            f" Auto Discover: {auto_discover}\n"
            f" Broadcast Port: {self.broadcast_port}\n"
            f" Broadcast Interval: {self.broadcast_interval}\n"
        )
        Logger().print_debug("#################################")

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
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_socket.bind(("0.0.0.0", self.broadcast_port))
        broadcast_socket.settimeout(self.broadcast_interval)

        while self.server_host is None:
            try:
                data, addr = broadcast_socket.recvfrom(1024)
                info = msgpack.unpackb(data)

                server_host = info["host"]
                pub_port = info["pub_port"]
                sub_port = info["sub_port"]

                if self.verbose:
                    Logger().print_debug(f"Discovered server: {server_host}, PUB:{pub_port}, SUB:{sub_port}")

                """
                Jason 2025-12-12:
                这里接收到的 pub_port 和 sub_port 是相对于服务器的端口，
                客户端需要连接到服务器的 pub_port 和 sub_port。
                也就是说，客户端的 PUB socket 连接到服务器的 SUB 端口，
                客户端的 SUB socket 连接到服务器的 PUB 端口。
                记得区分清楚！
                """
                self.server_host = server_host
                self.pub_port = sub_port
                self.sub_port = pub_port

                # 动态连接 ZMQ
                self._pub_socket.connect(f"tcp://{self.server_host}:{self.pub_port}")
                self._sub_socket.connect(f"tcp://{self.server_host}:{self.sub_port}")

                if self.verbose:
                    Logger().print_debug(f"Create client: {self.server_host}, PUB:{self.pub_port}, SUB:{self.sub_port}")

            except socket.timeout:
                continue
            except Exception as e:
                if self.verbose:
                    Logger().print_debug(f"Discovery error: {e}")
                continue

        broadcast_socket.close()

    def server_discovered(self) -> bool:
        return self.server_host is not None and self.pub_port is not None and self.sub_port is not None

    # --------------------------------------------------
    # 服务器 -> 客户端 接收数据
    # --------------------------------------------------
    def _sub_loop(self):
        while True:
            try:
                key_bytes, data_bytes = self._sub_socket.recv_multipart()
                key = key_bytes.decode()
                data = msgpack.unpackb(data_bytes)

                packet = {"key": key, "data": data}
                self._subscribe_handler(packet)

            except Exception as e:
                Logger().print_debug(f"{self.__class__.__name__} sub loop error: {e}")
                continue

    # --------------------------------------------------
    # 客户端 -> 服务器 发布数据
    # --------------------------------------------------
    def publish(self, key=None, value=None) -> FunctionResult:

        def convert_numpy_types(obj):
            if isinstance(obj, numpy.generic):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(i) for i in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_numpy_types(i) for i in obj)
            return obj

        if self.verbose:
            print(f"{self.__class__.__name__} publishing key={key} value={value}")

        # publish one key
        if key is not None and value is not None:
            try:
                data = msgpack.packb(value)
                self._pub_socket.send_multipart([key.encode(), data])
                return FunctionResult.SUCCESS
            except Exception as e:
                Logger().print_warning(f"{self.__class__.__name__} unhandled msgpack data = \n{key}\n{value}")
                return FunctionResult.FAIL

        # publish all keys
        data_dicts = {
            key: convert_numpy_types(getattr(self._dynalink_manager, f"dynalink_{key}").read_to_dict())
            for key in self.topic_keys
        }

        for key, data_dict in data_dicts.items():
            try:
                data = msgpack.packb(data_dict)
                self._pub_socket.send_multipart([key.encode(), data])
            except Exception as e:
                Logger().print_warning(f"{self.__class__.__name__} unhandled msgpack data = \n{key}\n{data_dict}")
                continue

        return FunctionResult.SUCCESS

    # --------------------------------------------------
    # 客户端->服务器 接收数据
    # --------------------------------------------------
    def _subscribe_handler(self, packet):
        key = packet.get("key")
        data = packet.get("data")

        if self.verbose:
            print(f"{self.__class__.__name__} subscribing key={key} data={data}")

        if key in self.topic_keys:
            getattr(self._dynalink_manager, f"dynalink_{key}").read_from_dict(data)

    # --------------------------------------------------
    # 单例 close
    # --------------------------------------------------
    def close(self):
        try:
            if getattr(self, "_pub_socket", None):
                self._pub_socket.close()
            if getattr(self, "_sub_socket", None):
                self._sub_socket.close()
            if getattr(self, "_context", None):
                self._context.term()
        except Exception:
            pass
