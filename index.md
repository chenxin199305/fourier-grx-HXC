---
layout: default
title: Fourier-GRX-HXC SDK
nav_order: 1
has_children: false
toc: true
toc_min_header: 2
toc_max_header: 3
---

# 欢迎来到 Fourier-GRX-HXC 文档站

Fourier-GRX-HXC SDK 是面向 **HXC T1 机器人** 的 `fourier-grx` 文档站，
用于说明 HXC 分支的安装、配置、运行和打包方式。

该分支保留了 HXC 运行所需的代码、资源和交付脚本，并通过 GitHub Pages 提供同仓库文档。

## 基本介绍

当前仓库主要面向：

- HXC T1 机器人运行与调试
- 打包生成 ZIP / DEB 交付物
- `fourier-core` 与主项目协同开发
- GitHub Pages 文档与代码同仓库维护

## 开始使用

[快速开始]({{ '/docs/quickstart/' | relative_url }}) 是开始使用 Fourier-GRX-HXC SDK 的推荐方式。
该分步指南会介绍环境准备、打包、安装与启动流程。

[参考指南]({{ '/docs/reference/' | relative_url }}) 汇总了配置文件、命令行入口、仓库结构与打包流程说明。

[常用操作]({{ '/docs/usage/' | relative_url }}) 说明安装后最常用的配置、查看和启动流程。

[常见问题]({{ '/docs/faq/' | relative_url }}) 汇总了 HXC 分支常见的安装、配置与运行问题。

[发布说明]({{ '/docs/release/' | relative_url }}) 记录文档站与运行产物的发布方式。

## 支持平台与版本

| 硬件环境 | 系统环境 | Python 环境 | 已测试 | 测试通过 |
| --- | --- | --- | --- | --- |
| X64 INTEL | Ubuntu 22.04 LTS | Python 3.11 | ✅ | ✅ |
| X64 AMD | Ubuntu 22.04 LTS | Python 3.11 | ✅ | ✅ |
| ARM64 | Ubuntu 22.04 LTS | Python 3.10 / 3.11 | | |

> ℹ️ **说明**:
>
> Fourier-GRX-HXC 当前文档主要聚焦 HXC 分支保留的运行与交付链路：
> - 启动配置位于 `config/hxc/`
> - 运行资源位于 `resource/hxc/`
> - `fourier-core/` 已作为普通子目录与主项目一同维护

## 更新日志

请查看 [更新日志]({{ '/docs/changelog/' | relative_url }}) 了解文档与仓库结构的变更情况。

## 贡献指南

请阅读 [贡献指南]({{ '/docs/contributing/' | relative_url }}) 以获取更多信息。

## 本地预览

```bash
bundle install
bundle exec jekyll serve --livereload
```

默认预览地址为 `http://127.0.0.1:4000/fourier-grx-HXC/`。
