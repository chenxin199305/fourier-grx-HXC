import time
import threading
import zmq
import msgpack
import socket
import numpy

from fourier_core.predefine import *
from fourier_core.logger import *

from fourier_grx.comm import *


class SyncServerZMQ:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(SyncServerZMQ, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
            host="0.0.0.0",
            pub_port=5566,
            sub_port=5567,
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
        self.host = host
        self.pub_port = pub_port
        self.sub_port = sub_port

        # ZeroMQ context
        self._context = zmq.Context()

        # PUB socket for server -> client
        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.bind(f"tcp://{host}:{pub_port}")

        # SUB socket for client -> server
        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.bind(f"tcp://{host}:{sub_port}")
        for key in self.topic_keys:
            self._sub_socket.setsockopt_string(zmq.SUBSCRIBE, key)

        # -----------------------------
        # 后台接收线程
        # -----------------------------
        self._sub_thread = threading.Thread(target=self._sub_loop, daemon=True)
        self._sub_thread.start()

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
            f"{self.__class__.__name__} ZMQ Config \n"
            f"PUB socket: tcp://{host}:{pub_port} \n"
            f"SUB socket: tcp://{host}:{sub_port} \n"
            f" Auto Discover: {auto_discover}\n"
            f" Broadcast Port: {self.broadcast_port}\n"
            f" Broadcast Interval: {self.broadcast_interval}\n"
        )
        Logger().print_debug("#################################")

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
                server_ip = self.host if self.host != "0.0.0.0" else socket.gethostbyname(socket.gethostname())
                data = msgpack.packb({"host": server_ip, "pub_port": self.pub_port, "sub_port": self.sub_port})
                broadcast_socket.sendto(data, ("255.255.255.255", self.broadcast_port))
                time.sleep(self.broadcast_interval)
            except Exception as e:
                continue

    # --------------------------------------------------
    # 接受数据（后台线程）
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
    # 服务器->客户端 发布数据
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
            except Exception:
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
            except Exception:
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
            getattr(self._dynalink_manager, f"dynalink_{key}").write_from_dict(data)

    # --------------------------------------------------
    # 关闭连接
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
