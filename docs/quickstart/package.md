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
| `make` | 完整 Nuitka 打包 | `dist/*.deb`、`dist/*.zip`、wheel |
| `make fast` | 基于 PyInstaller 的快速打包 | `dist/*.deb`、`dist/*.zip` |
| `make test` | 最快的测试型打包 | `dist/*-test.deb` |
| `make build` | 构建 wheel | `dist/fourier_grx-*.whl` |
| `make clean_all` | 清理主项目与 `fourier-core` 产物 | 清空 `build/`、`dist/` |

## 构建过程摘要

1. `update_env` 安装 `fourier-grx` 和 `fourier-core`。
2. `whl_file` 为两个包分别构建 wheel。
3. `bin_from_nuitka` 或 `bin_from_pyinstaller` 生成运行二进制。
4. `zip_bin[_whl]` 打包配置、资源、脚本和 wheel。
5. `deb_bin[_whl]` 生成 deb 安装包。

## 产物内容

ZIP/DEB 产物会把以下内容一起带上：

- `run.bin`
- `config/hxc/`
- `resource/hxc/`
- `resource/zenoh/`
- `release/` 下的安装与配置脚本
- `lib/`
- `fourier-core/dist/fourier_core-*.whl`

如果只需要本地开发，一般不必先打包，直接 `pip install -e .` 即可。
