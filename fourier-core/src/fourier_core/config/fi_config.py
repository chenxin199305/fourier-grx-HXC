import argparse
import json
import os
import sys
import yaml

from fourier_core.logger import *
from fourier_core.predefine import *


class FourierConfig:
    def __init__(self, config_file_path=None):
        # 如果没有指定配置文件路径，则检测命令行参数
        if config_file_path is None:
            # 检测命令行参数
            parser = argparse.ArgumentParser(description="Fourier Config File Parser")
            parser.add_argument(
                "--config",
                type=str,
                help="robot control system config file path",
                default="config.yaml"
            )
            args = parser.parse_args()

            config_file_path = args.config

        Logger().print_info(
            f"FourierConfig config_file_path = {config_file_path}"
        )

        # 检测文件名后缀
        if config_file_path.endswith(".json"):
            self.parameters = self.read_from_json(config_file_path)
        elif config_file_path.endswith(".yaml"):
            self.parameters = self.read_from_yaml(config_file_path)
        else:
            Logger().print_error(
                "FourierConfig Error: Invalid file type. Please use .json or .yaml file."
            )
            sys.exit(FunctionResult.FAIL)

        # 根据环境变量获取配置文件路径
        self.config_dir = os.getenv("FOURIER_CONFIG_PATH", os.getcwd())

    def read_from_json(self, path="config.json"):
        # get current file path
        current_workspace_path = os.getcwd()
        # Logger().print_info(f"current_workspace_path = {current_workspace_path}")

        # 读取根目录的配置文件
        if path.startswith("/"):
            config_json_path = path
        else:
            config_json_path = current_workspace_path + "/" + path

        Logger().print_info(
            f"FourierConfig config_file_absolute_path = {config_json_path}"
        )

        try:
            with open(config_json_path, encoding="utf-8") as json_file:
                parameters = json.load(fp=json_file)
        except Exception as e:
            Logger().print_error(
                f"FourierConfig {e} \n"
                f"Please check config file exist, and use --config to appoint the config file."
            )
            sys.exit(FunctionResult.FAIL)

        parameters = self.parse_parameters(parameters)

        # print json in beautiful format
        if parameters.get("log_config"):
            Logger().print_info("#################################")
            Logger().print_info(
                "FourierConfig config.json is: \n"
                f"{json.dump(parameters, indent=4, sort_keys=False)}"
            )
            Logger().print_info("#################################")

        return parameters

    def read_from_yaml(self, path="config.yaml"):
        # get current file path
        current_workspace_path = os.getcwd()
        # Logger().print_info(f"current_workspace_path = {current_workspace_path}")

        # 读取根目录的配置文件
        if path.startswith("/"):
            config_yaml_path = path
        else:
            config_yaml_path = current_workspace_path + "/" + path

        Logger().print_info(
            f"FourierConfig config_file_absolute_path = {config_yaml_path}"
        )

        try:
            with open(config_yaml_path) as yaml_file:
                parameters = yaml.load(yaml_file, Loader=yaml.FullLoader)
        except Exception as e:
            Logger().print_error(
                f"FourierConfig {e} \n"
                f"Please check config file exist, and use --config to appoint the config file."
            )
            sys.exit(FunctionResult.FAIL)

        parameters = self.parse_parameters(parameters)

        # print yaml in beautiful format
        if parameters.get("log_config"):
            Logger().print_info("#################################")
            Logger().print_info(
                f"FourierConfig config.yaml is: \n"
                f"{yaml.dump(parameters, indent=4, sort_keys=False)}"
            )
            Logger().print_info("#################################")

        return parameters

    def parse_parameters(self, parameters=None):
        """
        Two main functions:
        - Get value from config file by key, and automatically change certain values based on the key-value pair.
        - Set default value of the key-value pair if it is not in the config file.
        """
        if parameters is None:
            Logger().print_warning(
                "FourierConfig config file is empty, use default config parameters."
            )
            parameters = {"log_config": True}

        parameters_refine = parameters.copy()

        # get the value from the config file by key, if not exist, set default value
        # - Control System Layer
        log_config = parameters.get("log_config", False)
        log_level = parameters.get("log_level", "error")
        log_file = parameters.get("log_file", None)
        device_connected = parameters.get("device_connected", False)
        mode = parameters.get("mode", "debug")
        system = parameters.get("system", "Linux")

        hardware_type = parameters.get("hardware_type", "X64")
        hardware_layer = parameters.get("hardware_layer", "fourier-core")  # 默认使用 fourier-core 硬件层相关库

        # - Robot Layer
        peripheral = parameters.get("peripheral", {})

        peripheral_use_joystick = peripheral.get("use_joystick", False)
        peripheral_joystick_type = peripheral.get("joystick_type", "XBOX")  # support "XBOX", "PS4", "PS5", "GAMESIR"
        peripheral_use_keyboard = peripheral.get("use_keyboard", False)
        peripheral_keyboard_type = peripheral.get("keyboard_type", "STANDARD")  # support "STANDARD"

        peripheral_use_virtual_joystick = peripheral.get("use_virtual_joystick", False)
        peripheral_use_virtual_keyboard = peripheral.get("use_virtual_keyboard", False)
        peripheral_use_virtual_teleoperation = peripheral.get("use_virtual_teleoperation", False)
        peripheral_use_virtual_panel = peripheral.get("use_virtual_panel", False)
        peripheral_use_virtual_user = peripheral.get("use_virtual_user", False)

        # do something based on the key-value pair
        if log_level not in {"none", "trace", "highlight", "debug", "warning", "error"}:
            log_level = "error"

        if log_level == "none":
            Logger().set_level(LoggerLevel.NONE)
        elif log_level == "trace":
            Logger().set_level(LoggerLevel.TRACE)
        elif log_level == "debug":
            Logger().set_level(LoggerLevel.DEBUG)
        elif log_level == "info":
            Logger().set_level(LoggerLevel.INFO)
        elif log_level == "success":
            Logger().set_level(LoggerLevel.SUCCESS)
        elif log_level == "warning":
            Logger().set_level(LoggerLevel.WARNING)
        elif log_level == "error":
            Logger().set_level(LoggerLevel.ERROR)
        else:
            Logger().set_level(LoggerLevel.ERROR)

        if log_file is not None:
            log_file_name = log_file
            Logger().set_flag_log_file(flag=True, log_file_name=log_file_name)
        else:
            Logger().set_flag_log_file(flag=False)

        # save the parameters
        # - Control System Layer
        parameters_refine["log_config"] = log_config
        parameters_refine["log_level"] = log_level
        parameters_refine["log_file"] = log_file
        parameters_refine["device_connected"] = device_connected
        parameters_refine["hardware_type"] = hardware_type
        parameters_refine["system"] = system
        parameters_refine["mode"] = mode
        parameters_refine["hardware_layer"] = hardware_layer

        # - Robot Layer
        parameters_refine["peripheral"] = {}

        parameters_refine["peripheral"]["use_joystick"] = peripheral_use_joystick
        parameters_refine["peripheral"]["joystick_type"] = peripheral_joystick_type
        parameters_refine["peripheral"]["use_keyboard"] = peripheral_use_keyboard
        parameters_refine["peripheral"]["keyboard_type"] = peripheral_keyboard_type

        parameters_refine["peripheral"]["use_virtual_joystick"] = peripheral_use_virtual_joystick
        parameters_refine["peripheral"]["use_virtual_keyboard"] = peripheral_use_virtual_keyboard
        parameters_refine["peripheral"]["use_virtual_teleoperation"] = peripheral_use_virtual_teleoperation
        parameters_refine["peripheral"]["use_virtual_panel"] = peripheral_use_virtual_panel
        parameters_refine["peripheral"]["use_virtual_user"] = peripheral_use_virtual_panel

        return parameters_refine


# Singleton Object
gl_config = FourierConfig()
