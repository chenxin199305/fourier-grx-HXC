---
title: 运行命令
parent: 参考指南
nav_order: 2
---

# 运行命令

`fourier-grx` 的 DEB 入口由 `release/deb_run.sh` 提供，支持以下命令：

| 命令 | 作用 |
| --- | --- |
| `version` | 打印已安装版本 |
| `install` | 解压 ZIP 并完成安装初始化 |
| `uninstall` | 删除 `$HOME/fourier-grx` |
| `config` | 重新选择 HXC 配置变体 |
| `list` | 打印当前配置 |
| `start` | 启动控制程序 |
| `stop` | 停止控制程序 |
| `enable_service` | 启用开机自启动 |
| `disable_service` | 禁用开机自启动 |
| `background` | 后台启动 |
| `setup_conda` | 创建 Python 3.11 Conda 环境 |
| `setup_conda_py310` | 创建 Python 3.10 Conda 环境 |

## 关键脚本映射

| 命令 | 实际脚本 |
| --- | --- |
| `config` | `release/config.sh` |
| `list` | `release/list.sh` |
| `start` | `release/run.sh` |
| `enable_service` | `release/setup_enable_service.sh` |
| `disable_service` | `release/setup_disable_service.sh` |

源码开发时，你也可以直接阅读这些脚本来理解交付后的运行行为。
