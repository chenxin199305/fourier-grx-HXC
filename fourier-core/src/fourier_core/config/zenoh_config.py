import os
import traceback
import json
import yaml
import zenoh

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import *


class ZenohConfig:
    def __init__(self):

        # 初始化 ZenohConfig 对象，设置默认路径和用户凭据
        # 步骤1，默认先找 ~/fourier-grx/resource/zenoh 目录
        # 步骤2，如果没有找到，则使用 gl_config.parameters 中的 "zenoh" 字段的 "path" 值
        # 步骤3，如果 "path" 值为 None 或 "None"，则使用当前目录下的 resource/zenoh 目录

        self.authentication: bool = True
        self.default_path = os.path.join(
            os.path.expanduser("~"),
            "fourier-grx",
            "resource",
            "zenoh",
        )
        self.default_username: str = "fourier-grx"
        self.default_password: str = "fourier-grx"

        try:
            """
            Jason 2024-12-09:
            authentication 字段用于控制是否启用身份验证。
            """
            authentication = gl_config.parameters.get("zenoh", {}).get("authentication", False)

            self.set_authentication(bool(authentication))

            """
            Jason 2024-12-09:
            在 config.yaml 中 None 会被解析为 "None" 字符串
            """
            path = gl_config.parameters.get("zenoh", {}).get("path", None)

            Logger().print_debug(f"{self.__class__.__name__} "
                                 f"path from config: {path}")

            # 如果路径不存在，则使用默认路径
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
                    "zenoh",
                )

        except Exception as e:
            Logger().print_warning(f"{self.__class__.__name__} "
                                   f"path create fail! Set path to current dir path.")
            traceback.print_exception(e)

            # 如果发生异常，则使用当前路径
            path = os.path.join(
                os.path.abspath(os.path.curdir),
                "resource",
                "zenoh",
            )

        self.set_path(path)

        self.user_config_path = os.path.join(path, "user.yaml")
        self.credentials_config_path = os.path.join(path, "credentials.txt")

        self.user_config_parameters = {}

        # Load user config parameters, if not exists, create with default values
        if os.path.exists(self.user_config_path):
            with open(self.user_config_path) as file:
                self.user_config_parameters = yaml.load(file, Loader=yaml.FullLoader)

            if self.user_config_parameters is None:
                self.user_config_parameters = {}
        else:
            Logger().print_warning(f"{self.__class__.__name__} "
                                   f"user config file not found: {self.user_config_path}")

        # Update username and password from user config
        username = self.user_config_parameters.get("username", self.default_username)
        password = self.user_config_parameters.get("password", self.default_password)

        self.set_username(username)
        self.set_password(password)

        # Check if credentials file exists, if not, create it with default credentials
        if os.path.exists(self.credentials_config_path):
            pass
        else:
            Logger().print_warning(f"{self.__class__.__name__} "
                                   f"credentials file not found: {self.credentials_config_path}")

            if not os.path.exists(self.path):
                os.makedirs(self.path)
                Logger().print_info(f"{self.__class__.__name__} "
                                    f"path created: {self.path}")

            with open(self.credentials_config_path, "w+") as file:
                file.write(f"{self.username}:{self.password}\n")
                Logger().print_info(f"{self.__class__.__name__} "
                                    f"credentials file created: {self.credentials_config_path}")

    def set_authentication(self, authentication: bool):
        self.authentication = authentication

        Logger().print_debug(f"{self.__class__.__name__} "
                             f"authentication set: {authentication}")

    def set_username(self, username: str):
        self.username = username

        Logger().print_debug(f"{self.__class__.__name__} "
                             f"username set: {username}")

    def set_password(self, password: str):
        self.password = password

        Logger().print_debug(f"{self.__class__.__name__} "
                             f"password set: {password}")

    def set_path(self, path):
        self.path = path

        Logger().print_debug(f"{self.__class__.__name__} "
                             f"path set: {path}")

    def get_path(self):
        return self.path

    def get_config(self):
        """ Get zenoh.Config object with user credentials. """

        zenoh_config_json = {
            "mode": "peer",
        }

        # 如果不启用身份验证，则移除 auth 字段
        if self.authentication:
            zenoh_config_json["transport"] = {
                "auth": {
                    "usrpwd": {
                        "user": self.username,
                        "password": self.password,
                        "dictionary_file": self.credentials_config_path,
                    }
                },
            }

        else:
            pass

        """
        Jason 2025-06-30:
        每一次调用 zenoh.Config() 会创建一个新的 zenoh.Config 对象，拥有一个新的 id。
        如果绑定多个 session 为同一个 zenoh.Config 对象，可能会导致 session 间 id 冲突，通信异常。
        因此，建议在每次需要获取 zenoh.Config 时，都创建一个新的 zenoh.Config 对象。
        """
        zenoh_config = zenoh.Config.from_json5(
            json=json.dumps(zenoh_config_json)
        )

        return zenoh_config


gl_zenoh_config = ZenohConfig()
