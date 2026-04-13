#!/usr/bin/python
import sys
import time
import traceback

from loguru import logger

from .fi_log_font import LogFont
from .fi_logger_level import LoggerLevel


class Logger:
    STATE_OFF = 0x00
    STATE_ON = 0x01

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            cls._instance.flag_log_file = False
            cls._instance.flag_enable_extra = False

            cls._instance.state = Logger.STATE_ON
            cls._instance.level = LoggerLevel.NONE
            cls._instance.id = None
            cls._instance.extra = {"id": cls._instance.id}

            # change loguru logger style
            logger.remove()
            cls._instance.log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | {message}"
            cls._instance.logger_stdout_id = logger.add(sys.stdout, colorize=True, format=cls._instance.log_format)
            cls._instance.logger_file_id = 0
            cls._instance.log_file_name = None

            # change loguru logger level
            # TRACE | 5 |
            # DEBUG | 10 |
            # INFO | 20 |
            # SUCCESS | 25 |
            # WARNING | 30 |
            # ERROR | 40 |
            # CRITICAL | 50 |
            logger.level("INFO")

        return cls._instance

    def __init__(self):
        pass

    def set_level(self, level: LoggerLevel):
        self.level: LoggerLevel = level

        if self.level == LoggerLevel.NONE or self.level == LoggerLevel.TRACE:
            logger.level("TRACE")
        elif self.level == LoggerLevel.DEBUG:
            logger.level("DEBUG")
        elif self.level == LoggerLevel.INFO:
            logger.level("INFO")
        elif self.level == LoggerLevel.SUCCESS:
            logger.level("SUCCESS")
        elif self.level == LoggerLevel.WARNING:
            logger.level("WARNING")
        elif self.level == LoggerLevel.ERROR:
            logger.level("ERROR")
        elif self.level == LoggerLevel.CRITICAL:
            logger.level("CRITICAL")
        else:
            logger.level("ERROR")

        self.print_info(f"Logger: set level to {self.level.name}")

    def set_flag_log_file(self, flag=False, log_file_name: str = None):
        self.flag_log_file = flag

        if self.flag_log_file:
            if log_file_name is None:
                self.log_file_name = f"fourier_{time.strftime('%Y%m%d_%H%M%S')}.log"
            else:
                self.log_file_name = f"{log_file_name}_{time.strftime('%Y%m%d_%H%M%S')}.log"

            self.logger_file_id = \
                logger.add(self.log_file_name, level="INFO", colorize=False, format=self.log_format)
        else:
            if self.logger_file_id != 0:
                logger.remove(self.logger_file_id)
                self.logger_file_id = 0
            else:
                pass

        self.print_info(f"Logger: log to file {self.log_file_name}")

    def update_id(self, id=None):
        self.id = id
        self.extra.update({"id": str(self.id)})

        if self.id is not None:
            self.log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {extra} | <level>{level}</level> | {message}"
        else:
            self.log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | {message}"

        logger.remove(self.logger_stdout_id)
        self.logger_stdout_id = \
            logger.add(sys.stdout, colorize=True, format=self.log_format)

        if self.logger_file_id:
            logger.remove(self.logger_file_id)
            self.logger_file_id = \
                logger.add(self.log_file_name, level="INFO", colorize=False, format=self.log_format)

    # ------------------- 控制台打印 -------------------

    def _log(self, level, message, **kwargs):
        if self.state == Logger.STATE_ON:
            logger.bind(**self.extra).log(level, message, **kwargs)

    def _decorate(self, message, **kwargs):
        # check if kwargs contains "font" key
        if "font" in kwargs:
            font = kwargs.pop("font")
            log_font_set = LogFont.get_font(font)
            log_font_reset = LogFont.get_reset(font)
            if log_font_set is not None:
                message = f"{log_font_set}{message}{log_font_reset}"

        return message

    def _print(self, level, message, **kwargs):
        message = self._decorate(message, **kwargs)
        self._log(level=level, message=message, **kwargs)

        if level in ["ERROR", "CRITICAL"]:
            traceback.print_exc()

    def print(self, message, **kwargs):
        self._print("INFO", message, **kwargs)

    def print_trace(self, message, **kwargs):
        self._print("TRACE", message, **kwargs)

    def print_debug(self, message, **kwargs):
        self._print("DEBUG", message, **kwargs)

    def print_info(self, message, **kwargs):
        self._print("INFO", message, **kwargs)

    def print_success(self, message, **kwargs):
        self._print("SUCCESS", message, **kwargs)

    def print_warning(self, message, **kwargs):
        self._print("WARNING", message, **kwargs)

    def print_error(self, message, **kwargs):
        self._print("ERROR", message, **kwargs)

    def print_critical(self, message, **kwargs):
        self._print("CRITICAL", message, **kwargs)
