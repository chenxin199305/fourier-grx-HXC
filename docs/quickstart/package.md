---
title: 编译与打包
parent: 快速开始
nav_order: 2
---

# 编译与打包

仓库根目录 `Makefile` 提供了 HXC 分支的主要交付路径。

## 常用目标

| 命令 | 说明 | 产物 |
| --- | --- | --- |
| `make` / `make blaze` | Blaze 打包（约 5 分钟） | `dist/*-blaze.deb`、`dist/*.zip` |
| `make test` | 测试型打包，跳过 zip 重命名 | `dist/*-blaze.deb` |
| `make build` | 构建 wheel | `dist/fourier_grx-*.whl` |
| `make clean_all` | 清理主项目与 `fourier-core` 产物 | 清空 `build/`、`dist/` |

## 构建过程摘要

1. `update_env` 安装 `fourier-grx` 和 `fourier-core`（editable 模式）。
2. `bin_from_pyinstaller` 用 PyInstaller 生成 `dist/run.bin`。
3. `zip_bin` 打包配置、资源、脚本和驱动。
4. `deb_bin` 将 zip 封装为 deb 安装包。

## 产物内容

ZIP/DEB 产物包含：

- `run.bin`
- `config/hxc/`
- `resource/hxc/`
- `release/` 下的安装与配置脚本
- `lib/`

如果只需要本地开发，一般不必先打包，直接 `pip install -e .` 即可。
