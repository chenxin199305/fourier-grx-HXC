#!/bin/bash

# 判断是否有 $FOURIER_GRX_HOME 环境变量，如果没有则设置为 $HOME/fourier-grx
if [ -z $FOURIER_GRX_HOME ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

echo "=================================================="
echo "列出 fourier-grx 当前的配置项"
echo "=================================================="

# 读取 $FOURIER_GRX_HOME/run.sh 脚本中的配置项
robot_type=$(grep "robot_type=" $FOURIER_GRX_HOME/run.sh | cut -d "=" -f 2 | tr -d '\"')
robot_version=$(grep "robot_version=" $FOURIER_GRX_HOME/run.sh | cut -d "=" -f 2 | tr -d '\"')
run_type=$(grep "run_type=" $FOURIER_GRX_HOME/run.sh | cut -d "=" -f 2 | tr -d '\"')

# 修改 $FOURIER_GRX_HOME/run.sh 脚本中的机器人型号和版本
config_robot_type=$robot_type
config_robot_version=$robot_version
config_run_type=$run_type

# 获取得到配置文件的路径
robot_type_lowercase=$(echo $robot_type | tr '[:upper:]' '[:lower:]') # 将大写转换为小写
config_file_path=$FOURIER_GRX_HOME/config/${robot_type_lowercase}/config_${robot_type}_${robot_version}_${run_type}.yaml


echo ""
echo -e "config robot type: \033[32m$config_robot_type\033[0m"
echo -e "config robot version: \033[32m$config_robot_version\033[0m"
echo -e "config run type: \033[32m$config_run_type\033[0m"
echo -e "config file path: \033[32m$config_file_path\033[0m"
echo ""

exec bash
