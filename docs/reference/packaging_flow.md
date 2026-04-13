---
title: 打包链路
parent: 参考指南
nav_order: 4
---

# 打包链路

HXC 分支优先面向可交付运行包，而不是通用库发布。

## 主要设计点

`pyproject.toml` 的设计目标包括：

1. 把 `fourier-grx` 视为应用程序而非通用库。
2. 保持 PEP 517 / wheel 支持最小可用。
3. 将 Nuitka / PyInstaller 与 build backend 解耦。
4. 为 x86_64 / aarch64 提供 CPU-only torch wheels。

## 两条二进制构建路径

- **Nuitka**：默认正式交付路径，目标为单文件二进制。
- **PyInstaller**：快速构建路径，便于调试和验证。

## 构建入口

| 入口 | 位置 |
| --- | --- |
| Nuitka 配置 | `pyproject.toml -> [tool.nuitka]` |
| Nuitka 命令 | `pyproject.toml -> [tool.pdm.scripts].build_bin_nuitka` |
| PyInstaller 构建脚本 | `scripts/build_pyinstaller.py` |
| 打包编排 | `Makefile` |

## Pages 与代码共存

文档站构建不会参与 Python 打包流程：

- Jekyll 文件位于 `docs/`、`_includes/`、`_config.yaml`
- Python 打包排除 `docs`
- GitHub Pages 仅在 Actions 中构建 `_site`

因此文档和运行时代码可以在同一仓库中长期共存。
