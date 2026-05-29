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

# 安装 PyInstaller（USTC 镜像对该包有 403，强制使用官方 PyPI）
pip install pyinstaller==6.14.2 --index-url https://pypi.org/simple

# 进入 fourier-core 目录
cd ./fourier-core

# 安装依赖项（含 eclipse-zenoh 等二进制包，USTC 镜像有 403，强制使用官方 PyPI）
pip install -e . --index-url https://pypi.org/simple

# 返回上级目录
cd ..

# 安装 fourier-grx 依赖项（同上，避免 USTC 镜像 403 问题）
pip install -e . --index-url https://pypi.org/simple

exit 0  # 返回成功状态码