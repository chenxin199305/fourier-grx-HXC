#!/bin/bash

echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 为 fourier-grx 安装 Ubuntu 环境软件 \e[0m"
echo -e "\e[32m (安装过程需要网络连接) \e[0m"
echo -e "\e[32m Install Ubuntu environment software for fourier-grx \e[0m"
echo -e "\e[32m (Installation requires network connection) \e[0m"

# 检查是否网络连接正常
ping -c 3 www.baidu.com
if [ $? -ne 0 ]; then
    echo "
    网络连接不正常，环境软件安装跳过，请检查网络连接。
    如果程序运行不正常，请重新运行安装脚本。
    "
    exit 1
fi

# 更新软件包索引
sudo apt update -y
# sudo apt upgrade -y

# 安装必要软件包
sudo apt install vim -y
sudo apt install gedit -y
sudo apt install net-tools -y
sudo apt install iw -y # 网卡驱动安装需要
sudo apt install build-essential -y
sudo apt install openssh-server -y

