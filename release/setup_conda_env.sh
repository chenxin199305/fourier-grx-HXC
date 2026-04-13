#!/bin/bash

echo -e "\e[32m====================================================\e[0m"
echo -e "\e[32m 搭建 fourier-grx Conda 环境 \e[0m"
echo -e "\e[32m Setup fourier-grx Conda environment \e[0m"
echo -e "\e[32m====================================================\e[0m"

echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 请确保设备已连接到互联网 \e[0m"
echo -e "\e[32m Please ensure the device is connected to the internet \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

# 进入 $FOURIER_GRX_HOME/whl 目录
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 进入 $FOURIER_GRX_HOME/whl 目录 \e[0m"
echo -e "\e[32m Change directory to $FOURIER_GRX_HOME/whl \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

# 检测并设置 FOURIER_GRX_HOME 环境变量
if [ -z "$FOURIER_GRX_HOME" ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

# 检测目录是否存在
if [ ! -d "$FOURIER_GRX_HOME/whl" ]; then
    echo -e "\e[31m错误：未找到 $FOURIER_GRX_HOME/whl 目录，请确认 fourier-grx 已正确安装\e[0m"
    exit 1
fi

cd "$FOURIER_GRX_HOME/whl" || exit

# 下载 Miniconda 安装包
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 下载 Miniconda 安装包 \e[0m"
echo -e "\e[32m Download Miniconda installer \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

if [ -d "$HOME/miniconda3" ]; then
    echo "Miniconda 已安装"
else

    if [ -f "Miniconda3-latest-Linux-x86_64.sh" ]; then
        echo "Miniconda 安装包已存在"
    else
        if ! wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh; then
            echo -e "\e[31m错误：Miniconda 下载失败\e[0m"
            exit 1
        fi
    fi

fi

# 安装 Miniconda
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 安装 Miniconda \e[0m"
echo -e "\e[32m Install Miniconda \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

if [ -d "$HOME/miniconda3" ]; then
    echo "Miniconda 已安装"
else
    bash Miniconda3-latest-Linux-x86_64.sh -b -p "$HOME/miniconda3" || exit
fi

# 初始化 Conda
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 初始化 Conda 环境 \e[0m"
echo -e "\e[32m Initialize Conda \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

# 确保 conda 命令可用
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# 将 conda 初始化添加到 bashrc（如果尚未添加）
if ! grep -q "conda initialize" "$HOME/.bashrc"; then
    "$HOME/miniconda3/bin/conda" init bash
fi

# 创建 Conda 环境
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 创建 Conda 环境 \e[0m"
echo -e "\e[32m Create Conda environment \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "如果遇到安装错误，终止了安装，请运行 exec bash 重新加载环境，然后重新运行此脚本/命令行。"

echo -e "设定接受 Conda 许可协议 （最新 conda 安装要求）"
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

if conda env list | grep -q "fourier-grx"; then
    echo "Conda 环境 fourier-grx 已存在"
else
    conda create -n fourier-grx python=3.11 -y || exit
fi

# 激活 Conda 环境
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 激活 Conda 环境 \e[0m"
echo -e "\e[32m Activate Conda environment \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

conda activate fourier-grx || exit

# 安装依赖包
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 安装依赖包 \e[0m"
echo -e "\e[32m Install dependencies \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

# 安装 CPU 版本 torch
pip install torch==2.6.0+cpu --index-url https://download.pytorch.org/whl/cpu || exit

# 安装 fourier-grx 依赖包
pip install fourier_core-*.whl || exit
pip install fourier_grx-*.whl || exit

# 提示安装完成
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 安装完成 \e[0m"
echo -e "\e[32m Installation completed \e[0m"
echo -e "\e[32m----------------------------------------------------\e[0m"

# 打印 conda 环境信息
conda env list

echo "具体程序使用方法请参考 Fourier GRX 文档"
echo "Please refer to the Fourier GRX documentation for specific usage"
