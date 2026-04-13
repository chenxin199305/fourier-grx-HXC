---
title: 常用操作
nav_order: 2
---

# 常用操作

HXC 分支保留的是面向现场运行和打包的最小闭环，常见操作主要围绕安装、配置、查看配置和启动程序展开。

## 选择运行配置

安装过程中的 `fourier-grx config` 会提示两种配置变体：

1. `HXC T1 Debug`
2. `HXC T1 Offline`

它们分别对应：

- `config/hxc/config_HXC_T1_debug.yaml`
- `config/hxc/config_HXC_T1_offline.yaml`

## 查看当前配置

```bash
fourier-grx list
```

该命令会从 `run.sh` 中解析当前值，并打印：

- robot type
- robot version
- run type
- 最终使用的配置文件路径

## 配置开机自启动

```bash
fourier-grx enable_service
fourier-grx disable_service
```

对应脚本位于：

- `release/setup_enable_service.sh`
- `release/setup_disable_service.sh`

## 后台运行

```bash
fourier-grx background
```

该命令通过 `nohup` 后台启动 `run.sh`，可避免终端关闭后程序退出。

## 一键配置 Conda 环境

```bash
fourier-grx setup_conda
fourier-grx setup_conda_py310
```

分别对应 Python 3.11 与 Python 3.10 的配套环境脚本。
