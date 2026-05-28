#!/bin/bash

# 判断是否有 $FOURIER_GRX_HOME 环境变量，如果没有则设置为 $HOME/fourier-grx
if [ -z $FOURIER_GRX_HOME ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

echo "=================================================="
echo "配置 fourier-grx"
echo "=================================================="

echo "--------------------------------------------------"
echo "当前仓库仅保留 HXC 相关配置"
echo "请选择配置变体"
echo "1. HXC T1"
echo "--------------------------------------------------"
read -p "请输入数字[1]选择配置变体: " config_variant

case $config_variant in
    1)
        robot_type="HXC"
        robot_version="T1"
        additional_version=""
        ;;
    *)
        echo "输入错误，退出安装"
        exit 1
        ;;
esac

echo "--------------------------------------------------"
echo "运行模式"
echo "1. 调试模式"
echo "2. 离线调试模式"
echo "--------------------------------------------------"
read -p "请输入数字[1-2]选择运行模式: " run_mode

case $run_mode in
    1)
        run_type="debug"
        ;;
    2)
        run_type="offline"
        ;;
    *)
        echo "输入错误，退出安装"
        exit 1
        ;;
esac

# 修改 $FOURIER_GRX_HOME/run.sh 脚本中的机器人型号和版本
config_robot_type=$robot_type
config_robot_version=$robot_version$additional_version
config_run_type=$run_type

echo ""
echo -e "config robot type: \033[32m$config_robot_type\033[0m"
echo -e "config robot version: \033[32m$config_robot_version\033[0m"
echo -e "config run type: \033[32m$config_run_type\033[0m"
echo ""

sed -i "s|^robot_type=.*|robot_type=\"${config_robot_type}\"|" "$FOURIER_GRX_HOME/run.sh"
sed -i "s|^robot_version=.*|robot_version=\"${config_robot_version}\"|" "$FOURIER_GRX_HOME/run.sh"
sed -i "s|^run_type=.*|run_type=\"${config_run_type}\"|" "$FOURIER_GRX_HOME/run.sh"

# 完成配置
echo ""
echo "--------------------------------------------------"
echo "运行 fourier-grx start 启动机器人控制程序"

exec bash
