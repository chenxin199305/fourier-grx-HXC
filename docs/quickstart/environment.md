---
title: 环境准备
parent: 快速开始
nav_order: 1
---

# 环境准备

`fourier-grx-HXC` 推荐在 Ubuntu 22.04 上开发，GLIBC 版本要求为 2.34 及以上。

## 从源码启动开发环境

```bash
conda create -n fourier-grx python=3.11
conda activate fourier-grx
pip install -e .
cd fourier-core && pip install -e .
```

如果希望按照仓库脚本一次性完成环境准备，可使用根目录脚本：

```bash
bash install_env.sh
```

该脚本会依次执行：

1. `shells/dependencies.sh` 安装依赖。
2. `shells/create_resource_link.sh` 创建资源软链接。
3. `shells/create_config_link.sh` 创建配置软链接。
4. `shells/setup_conda_env.sh` 更新 Conda 环境。

## 关键依赖

主项目使用 `pyproject.toml` 管理依赖，核心运行时包括：

- `typer`、`loguru`、`omegaconf`
- `eclipse-zenoh`、`pygame`、`inputs`
- `pin`、`pin-pink`、`ruckig`、`qpsolvers`
- `torch` CPU wheels
- `fourier-core`

`fourier-core` 现在是当前仓库内的普通子目录，`make update_env` 会同时以 editable 方式安装主项目和 `fourier-core`。
