# fourier-grx

[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://docs.python.org/3/whatsnew/3.10.html)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://docs.python.org/3/whatsnew/3.11.html)

> HXC-only branch: this branch keeps only the code and assets required for the HXC robot runtime and packaging flow.

## 系统环境要求

fourier-grx 建议使用 Ubuntu 22.04 系统进行开发，使用的 GLIBC 版本为 2.34 以上版本。

## 快速开始

```
# 1. 创建conda虚拟环境
conda create -n fourier-grx python=3.11

# 2. 安装依赖
pip install -e .

# 3. 编译打包 (打包后的文件会在dist目录下)
#    打包方式有多种，针对不同情况使用，具体可以参考 Makefile 内容：
#    1. make: 完整打包（较慢，30min+），包含所有依赖和二次开发库，输出二进制内容的 deb 包
#    2. make fast: 快速打包（较快，15min+），包含所有依赖和二次开发库，输出带源码内容的 deb 包
#    3. make test: 测试打包（最快，5min+），包含所有依赖，不含二次开发库，输出带源码内容的 deb 包
make

# 4. 安装程序
sudo dpkg -i fourier-grx-x.x.x.deb
fourier-grx install

# 5. 运行程序
fourier-grx start
```

## 使用说明

本分支默认面向 HXC T1。常用启动配置位于 `config/hxc/`，资源位于 `resource/hxc/`。
