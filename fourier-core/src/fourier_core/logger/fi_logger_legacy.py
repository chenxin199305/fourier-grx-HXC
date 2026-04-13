#!/usr/bin/python
import logging
import os
import platform
import sys
import time

from .fi_logger_level import LoggerLevel


class Logger:
    STATE_OFF = 0x00
    STATE_ON = 0x01

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            cls._instance.flag_log_file = False

            cls._instance.state = Logger.STATE_ON
            cls._instance.level = LoggerLevel.NONE

        return cls._instance

    def __init__(self):
        self.__init_log()

    def set_level(self, level: LoggerLevel):
        self.level: LoggerLevel = level

    def set_flag_log_file(self, flag: bool):
        self.flag_log_file = flag

    def __init_log(self):
        # Check if the log file is inited
        if self.flag_log_file:
            pass
        else:
            return None

        # Log file create
        LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s"
        DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
        # INFO DEBUG WARNING ERROR CRITICAL
        LOG_LEVEL = logging.INFO

        project_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件路径的上一级目录
        exe_file_path = project_path
        print(exe_file_path)

        sysstr = platform.system()
        if sysstr == "Windows":
            self.is_windows_flag = True
        else:
            self.is_windows_flag = False

        if self.is_windows_flag == True:
            path = exe_file_path + "\\log\\"
            name = str(rf"{time.localtime().tm_year:02d}\{time.localtime().tm_mon:02d}\\")
        else:
            path = "./log/"
            name = str(f"{time.localtime().tm_year:02d}/{time.localtime().tm_mon:02d}/")

        self.log_dir_path = path + name

        isExists = os.path.exists(self.log_dir_path)
        if not isExists:
            os.makedirs(self.log_dir_path)
            print("Log Created", self.log_dir_path)
        else:
            print("Log Already Existed", self.log_dir_path)

        self.log_name = str(
            f"{time.localtime().tm_year:02d}_{time.localtime().tm_mon:02d}_{time.localtime().tm_mday:02d}_{time.localtime().tm_hour:02d}.{time.localtime().tm_min:02d}.{time.localtime().tm_sec:02d}"
        )
        self.log_dir = self.log_dir_path + self.log_name + ".log"

        logging.basicConfig(
            filename=self.log_dir,
            level=LOG_LEVEL,
            format=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
        logging.log(logging.INFO, "\n\n########## The robot is starting !!! ##########\n\n\n")

    # 设置时间戳最小单位
    # unit='us' 'ms' 's'
    def __time(self, unit="us"):
        if unit == "ms" or unit == "us":
            t = time.time()
            tmid = int(t * 1000000 % 1000000)
            tms = int(tmid / 1000 % 1000)
            t_get = time.localtime(t)
            if unit == "us":
                tus = int(tmid % 1000)
                t_usr = [
                    t_get.tm_year,
                    t_get.tm_mon,
                    t_get.tm_mday,
                    t_get.tm_hour,
                    t_get.tm_min,
                    t_get.tm_sec,
                    tms,
                    tus,
                ]
                t_usr_time_str = (
                        str(t_usr[0]).rjust(4)
                        + "."
                        + str(t_usr[1]).rjust(2, "0")
                        + "."
                        + str(t_usr[2]).rjust(2, "0")
                        + " "
                        + str(t_usr[3]).rjust(2, "0")
                        + ":"
                        + str(t_usr[4]).rjust(2, "0")
                        + ":"
                        + str(t_usr[5]).rjust(2, "0")
                        + "."
                        + str(t_usr[6]).rjust(3, "0")
                        + "."
                        + str(t_usr[7]).rjust(3, "0")
                )
            else:
                t_usr = [
                    t_get.tm_year,
                    t_get.tm_mon,
                    t_get.tm_mday,
                    t_get.tm_hour,
                    t_get.tm_min,
                    t_get.tm_sec,
                    tms,
                ]
                t_usr_time_str = (
                        str(t_usr[0]).rjust(4)
                        + "."
                        + str(t_usr[1]).rjust(2, "0")
                        + "."
                        + str(t_usr[2]).rjust(2, "0")
                        + " "
                        + str(t_usr[3]).rjust(2, "0")
                        + ":"
                        + str(t_usr[4]).rjust(2, "0")
                        + ":"
                        + str(t_usr[5]).rjust(2, "0")
                        + "."
                        + str(t_usr[6]).rjust(3, "0")
                )
            return '\033[0;32m' + t_usr_time_str + "\033[0m" + ' |'
        else:
            now = '\033[0;32m' + time.strftime("%Y-%m-%d %H:%M:%S") + "\033[0m" + ' |'
        return now

    # ------------------- 文件打印 -------------------

    def print_log_file_debug(self, str_temp):
        self.__init_log()
        logging.log(logging.DEBUG, str_temp)

    def print_log_file_info(self, str_temp):
        self.__init_log()
        logging.log(logging.INFO, str_temp)

    def print_log_file_warning(self, str_temp):
        self.__init_log()
        logging.log(logging.WARNING, str_temp)

    def print_log_file_error(self, str_temp):
        self.__init_log()
        logging.log(logging.ERROR, str_temp)

    def print_log_file_critical(self, str_temp):
        self.__init_log()
        logging.log(logging.CRITICAL, str_temp)

    def print_log_file_data(self, data_list: list):
        self.__init_log()
        # open log file and write data as csv
        with open(self.log_dir, "a") as f:
            f.write(self.__time() + ",")
            for data in data_list:
                f.write(str(data) + ",")
            f.write("\n")

    # ------------------- 控制台打印 -------------------

    def print(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_line(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            print(*objects, sep=sep, end=end, file=file, flush=flush)

    # 设置控制台显示颜色
    # 显示方式: 0（默认值）、1（粗体）、22（非粗体）、4（下划线）、24（非下划线）、 5（闪烁）、25（非闪烁）、7（反显）、27（非反显）
    # 前景色: 30（黑色）、31（红色）、32（绿色）、 33（黄色）、34（蓝色）、35（洋 红）、36（青色）、37（白色）
    # 背景色: 40（黑色）、41（红色）、42（绿色）、 43（黄色）、44（蓝色）、45（洋 红）、46（青色）、47（白色）
    # 常见开头格式：
    # \033[0m            默认字体正常显示，不高亮
    # \033[0;31m       红色字体正常显示
    # \033[1;32;40m  显示方式: 高亮    字体前景色：绿色  背景色：黑色
    # \033[0;31;46m  显示方式: 正常    字体前景色：红色  背景色：青色
    def print_trace(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.TRACE:
                now = self.__time()
                print(now, "\033[1mINFO   \033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_success(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.SUCCESS:
                now = self.__time()
                print(now, "\033[1;32mSUCCESS\033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_debug(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.DEBUG:
                now = self.__time()
                print(now, "\033[1mDEBUG  \033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_warning(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.WARNING:
                now = self.__time()
                print(now, "\033[1;33mWARNING\033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_error(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.ERROR:
                now = self.__time()
                print(now, "\033[1;31mERROR  \033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)

    def print_critical(self, *objects, sep=" ", end="\n", file=sys.stdout, flush=False, **kwargs):
        if self.state == Logger.STATE_ON:
            if self.level <= LoggerLevel.CRITICAL:
                now = self.__time()
                print(now, "\033[1;31mCRITICAL\033[0m |", end=' ')
                print(*objects, sep=sep, end=end, file=file, flush=flush)
