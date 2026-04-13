---
title: 仓库结构
parent: 参考指南
nav_order: 3
---

# 仓库结构

仓库同时承载代码、打包脚本和 GitHub Pages 文档站。

## 顶层目录说明

| 路径 | 说明 |
| --- | --- |
| `src/fourier_grx/` | 主项目源码 |
| `fourier-core/` | 与主仓库共存的底层核心代码 |
| `config/hxc/` | HXC T1 配置文件 |
| `resource/hxc/` | HXC 运行资源 |
| `resource/zenoh/` | Zenoh 认证与用户配置 |
| `release/` | 安装、配置、打包及运行脚本 |
| `scripts/` | 构建辅助脚本 |
| `docs/` | GitHub Pages 文档内容 |
| `_config.yaml` | Jekyll 站点配置 |
| `.github/workflows/pages.yml` | GitHub Pages 发布工作流 |

## 关于 `fourier-core`

`fourier-core/` 现在是当前仓库中的普通子目录，而不是 Git submodule。这意味着：

- 可与主项目一起提交和审阅变更；
- `make update_env` 与 `make whl_file` 会同时处理两个包；
- GitHub Pages 文档也可以直接引用该目录结构，无需额外说明 submodule 初始化步骤。
