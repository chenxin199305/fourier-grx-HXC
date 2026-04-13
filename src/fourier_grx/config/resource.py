import os
import traceback

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *


class Resource:
    def __init__(self):

        robot_name = gl_config.parameters.get("robot", {}).get("name", None)

        if robot_name is None:
            robot_name = "none"

        # 初始化 Resource 对象，设置默认路径
        # 步骤1，默认先找 ~/fourier-grx/resource/robot_name 目录
        # 步骤2，如果没有找到，则使用 gl_config.parameters 中的 "resource" 字段的 "path" 值
        # 步骤3，如果 "path" 值为 None 或 "None"，则使用当前目录下的 resource/robot_name 目录

        self.default_path = os.path.join(
            os.path.expanduser("~"),
            "fourier-grx",
            "resource",
            str.lower(robot_name),
        )

        try:
            """
            Jason 2024-12-09:
            在 config.yaml 中 None 会被解析为 "None" 字符串
            """
            path = gl_config.parameters.get("resource", {}).get("path", None)

            Logger().print_debug(f"{self.__class__.__name__} "
                                 f"path in config: {path}, "
                                 f"robot name: {robot_name}")

            if path is None or path == "None":
                path = self.default_path

            else:
                # 解析 "~" 为用户目录
                path = os.path.expanduser(path)

            # 如果路径不存在，则使用当前路径
            if not os.path.exists(path):
                Logger().print_warning(f"{self.__class__.__name__} "
                                       f"path {path} not exists! "
                                       f"Set to use current dir path.")

                path = os.path.join(
                    os.path.abspath(os.path.curdir),
                    "resource",
                    str.lower(robot_name),
                )

        except Exception as e:
            Logger().print_warning(f"{self.__class__.__name__} "
                                   f"path create fail! Set path to current dir path.")
            traceback.print_exception(e)

            # 如果发生异常，则使用当前路径
            path = os.path.join(
                os.path.abspath(os.path.curdir),
                "resource",
                str.lower(robot_name),
            )

        self.set_path(path)

    def set_path(self, path):
        self.path = path

        Logger().print_debug(f"{self.__class__.__name__} path set: {path}")

    def get_path(self):
        return self.path


_gl_resource = None


def __getattr__(name: str):
    global _gl_resource
    if name == "gl_resource":
        if _gl_resource is None:
            _gl_resource = Resource()
        return _gl_resource
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
