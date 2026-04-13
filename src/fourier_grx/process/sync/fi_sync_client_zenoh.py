import numpy
import zenoh
import msgpack
import json

from fourier_core.predefine import *
from fourier_core.logger import *
from fourier_core.config.zenoh_config import gl_zenoh_config

from fourier_grx.comm import *


class SyncClientZenoh:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(SyncClientZenoh, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
            self,
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

        # 构建 Zenoh 节点
        self.zenoh_prefix = "fourier-grx"
        self.zenoh_root = "/dynalink_interface"
        self.zenoh_suffix = ""
        self.zenoh_key_exprs = {}

        # 初始化 Zenoh 会话
        self._session: zenoh.Session = zenoh.open(gl_zenoh_config.get_config())

        # Publisher / Subscriber / Service
        self._publishers: dict[str, zenoh.Publisher] = {}
        self._subscribers: dict[str, zenoh.Subscriber] = {}
        self._services: dict[str, zenoh.Queryable] = {}

        # 创建 publisher / subscriber
        for key in self.topic_keys:
            key_expr_core = (
                    f"{self.zenoh_prefix}{self.zenoh_root}{self.zenoh_suffix}" +
                    (f"/{key}" if key else "")
            )

            # publisher(client)
            self._publishers[key] = self._session.declare_publisher(
                key_expr=f"{key_expr_core}/client",
                priority=zenoh.Priority.REAL_TIME,
                congestion_control=zenoh.CongestionControl.DROP,
                reliability=zenoh.Reliability.BEST_EFFORT,
            )

            # subscriber(server)
            self._subscribers[key] = self._session.declare_subscriber(
                key_expr=f"{key_expr_core}/server",
                handler=self._subscribe_handler,
            )

        # 打印 key expr 信息
        self.zenoh_key_exprs = {
            "publishers": {key: str(self._publishers[key].key_expr) for key in self.topic_keys},
            "subscribers": {key: str(self._subscribers[key].key_expr) for key in self.topic_keys},
            "services": {},
        }

        Logger().print_debug("#################################")
        Logger().print_debug(
            f"{self.__class__.__name__} Zenoh Config \n"
            f"authentication: {gl_zenoh_config.authentication} \n"
            f"username: {gl_zenoh_config.username} \n"
            f"password: {gl_zenoh_config.password} \n"
            f"credentials_config_path: {gl_zenoh_config.credentials_config_path} \n"
            f"zenoh_key_exprs : \n"
            f"{json.dumps(self.zenoh_key_exprs, indent=4, ensure_ascii=False)}"
        )
        Logger().print_debug("#################################")

    # --------------------------------------------------
    # 单例析构：关闭 Session
    # --------------------------------------------------
    def __del__(self):
        self.close()

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
            data = msgpack.packb(value)
            if key in self._publishers:
                self._publish_handler(self._publishers[key], data)
                return FunctionResult.SUCCESS
            return FunctionResult.FAIL

        # publish all keys
        data_dicts = {
            key: convert_numpy_types(getattr(self._dynalink_manager, f"dynalink_{key}").write_to_dict())
            for key in self.topic_keys
        }

        for key, data_dict in data_dicts.items():
            try:
                data = msgpack.packb(data_dict)
            except Exception:
                print(f"{self.__class__.__name__} unhandled msgpack data = \n{key}\n{data_dict}")
                continue
            self._publish_handler(self._publishers[key], data)

        return FunctionResult.SUCCESS

    def _publish_handler(self, publisher, data):
        publisher.put(data)

    # --------------------------------------------------
    # 服务器 -> 客户端 接收数据
    # --------------------------------------------------
    def _subscribe_handler(self, sample: zenoh.Sample):
        key_expr = sample.key_expr
        sample_value = sample.payload.to_bytes()
        data_dict = msgpack.unpackb(sample_value)

        key_map = {
            f"{self.zenoh_prefix}{self.zenoh_root}{self.zenoh_suffix}/{key}/server":
                getattr(self._dynalink_manager, f"dynalink_{key}")
            for key in self.topic_keys
        }

        if key_expr in key_map:
            key_map[key_expr].read_from_dict(data_dict)

    # --------------------------------------------------
    # 单例 close
    # --------------------------------------------------
    def close(self):
        try:
            if getattr(self, "_session", None):
                self._session.close()
        except Exception:
            pass
