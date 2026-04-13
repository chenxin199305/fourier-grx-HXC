#!/bin/bash

set -e  # 在任意命令出错时立即退出

# install build tools
sudo apt update
sudo apt install build-essential -y
sudo apt install gfortran -y

# 更新 pip 和 setuptools
pip install --upgrade pip setuptools

# 安装 pdm
pip install pdm

# 安装 PyInstaller
pip install pyinstaller==6.14.2

# 进入 fourier-core 目录
cd ./fourier-core

# 安装依赖项
pip install -e .

# 返回上级目录
cd ..

# 安装 fourier-grx 依赖项
pip install -e .

exit 0  # 返回成功状态码