#!/bin/bash

# 判断是否有 $FOURIER_GRX_HOME 环境变量，如果没有则设置为 $HOME/fourier-grx
if [ -z $FOURIER_GRX_HOME ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

echo -e "\e[32m====================================================\e[0m"
echo -e "\e[32m 安装依赖环境 \e[0m"
echo -e "\e[32m Install dependent environment \e[0m"
echo -e "\e[32m====================================================\e[0m"

chmod +x $FOURIER_GRX_HOME/script/setup_ubuntu_env.sh
$FOURIER_GRX_HOME/script/setup_ubuntu_env.sh

chmod +x $FOURIER_GRX_HOME/script/setup_pass_sudo.sh
$FOURIER_GRX_HOME/script/setup_pass_sudo.sh

chmod +x $FOURIER_GRX_HOME/script/setup_disable_ipv6.sh
$FOURIER_GRX_HOME/script/setup_disable_ipv6.sh

chmod +x $FOURIER_GRX_HOME/script/setup_static_ipv4.sh
$FOURIER_GRX_HOME/script/setup_static_ipv4.sh

echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 修改 run.sh 的权限，方便后续运行 \e[0m"
echo -e "\e[32m Change the permission of run.sh for later execution \e[0m"

chmod +x $FOURIER_GRX_HOME/run.sh
