#!/bin/bash

# 判断是否有 $FOURIER_GRX_HOME 环境变量，如果没有则设置为 $HOME/fourier-grx
if [ -z $FOURIER_GRX_HOME ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

# ------------------------------------------------------
# 请确认配置项

# 设置是否开机自启动 fourier-grx
auto_start=1  # 1: 启动  0: 不启动

# 目前支持的机器人类型和版本
# robot_type - robot_version
# "HXC" - "T1"
robot_type="HXC"  # 机器人名称
robot_version="T1"  # 机器人版本

# 运行模式
# debug: 调试模式
# offline: 离线调试模式
run_type="debug"

# ------------------------------------------------------

robot_type_lowercase=$(echo $robot_type | tr '[:upper:]' '[:lower:]') # 将大写转换为小写

if [ $auto_start -eq 0 ]; then
    echo -e "\e[31m ================================================== \e[0m"
    echo -e "\e[31m fourier-grx Auto Execution is not enabled \e[0m"
    echo -e "\e[31m ================================================== \e[0m"
    exit 1
fi

# 判断是否安装了 fourier-grx
if [ ! -f $FOURIER_GRX_HOME/run.bin ]; then
    echo -e "\e[31m ================================================== \e[0m"
    echo -e "\e[31m fourier-grx is not installed, please install it first \e[0m"
    echo -e "\e[31m ================================================== \e[0m"
    exit 2
fi

echo -e "\e[32m ================================================== \e[0m"
echo -e "\e[32m fourier-grx Auto Execution \e[0m"
echo -e "\e[32m running in $run_type mode \e[0m"
echo -e "\e[32m ================================================== \e[0m"

# run the script, store the output in a log file
run_time=$(date "+%Y_%m_%d_%H_%M_%S")
log_file_name="${run_time}.log"

echo "Log file: $FOURIER_GRX_HOME/${log_file_name}"

mkdir -p $FOURIER_GRX_HOME/log

config_file_path=$FOURIER_GRX_HOME/config/${robot_type_lowercase}/config_${robot_type}_${robot_version}_${run_type}.yaml

stdbuf -oL $FOURIER_GRX_HOME/run.bin --config=${config_file_path} \
| tee $FOURIER_GRX_HOME/log/${log_file_name}

exit 0
