---
layout: default
title: 常用操作
nav_order: 5
has_toc: true
---

# 常用操作

* TOC
{:toc}

本文档介绍使用 Fourier-GRX-HXC SDK 时最常见的操作流程。

## 选择运行配置

`fourier-grx config` 当前提供两种 HXC 变体：

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

## 启动程序

```bash
fourier-grx start
```

运行时会根据 `run.sh` 中的 `robot_type`、`robot_version` 和 `run_type` 选择配置文件并启动 `run.bin`。

## 后台运行

```bash
fourier-grx background
```

该命令通过 `nohup` 后台启动 `run.sh`，可避免终端关闭后程序退出。

## 配置开机自启动

```bash
fourier-grx enable_service
fourier-grx disable_service
```

对应脚本位于：

- `release/setup_enable_service.sh`
- `release/setup_disable_service.sh`

## 一键配置 Conda 环境

```bash
fourier-grx setup_conda
fourier-grx setup_conda_py310
```

分别对应 Python 3.11 与 Python 3.10 的配套环境脚本。
