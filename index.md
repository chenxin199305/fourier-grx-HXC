---
title: Fourier-GRX-HXC SDK
nav_order: 0
has_children: false
---

# 欢迎来到 Fourier-GRX-HXC 文档站

本仓库是面向 **HXC T1 机器人** 的 `fourier-grx` 精简分支，保留了机器人运行、配置、资源和打包流程所需的代码与资产。

文档站与源代码共存在同一仓库中，可直接通过 GitHub Pages 发布。

## 文档导航

- [快速开始]({{ '/docs/quickstart/' | relative_url }})：环境准备、打包、安装与启动流程。
- [常用操作]({{ '/docs/usage/' | relative_url }})：安装后常见的配置、列举和运行步骤。
- [参考指南]({{ '/docs/reference/' | relative_url }})：配置文件、命令行入口、目录结构与打包链路说明。
- [常见问题]({{ '/docs/faq/' | relative_url }})：HXC 分支常见排查思路。
- [发布说明]({{ '/docs/release/' | relative_url }})：GitHub Pages 和二进制产物的发布方式。
- [贡献指南]({{ '/docs/contributing/' | relative_url }})：如何补充代码与文档。

## 当前分支特点

- 仅保留 HXC 相关配置，启动配置位于 `config/hxc/`。
- HXC 运行资源位于 `resource/hxc/`，Zenoh 配置位于 `resource/zenoh/`。
- `fourier-core/` 以同仓库子目录形式存在，可与主项目一起编辑、打包和发布。

## 推荐平台

| 项目 | 建议值 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| Python | 3.10 / 3.11 |
| GLIBC | 2.34+ |
| 目标机器人 | HXC T1 |

## 本地预览文档

```bash
bundle install
bundle exec jekyll serve --livereload
```

默认首页地址为 `http://127.0.0.1:4000/fourier-grx-HXC/`。
