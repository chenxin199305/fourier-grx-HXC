---
layout: default
title: 常见问题
nav_order: 6
has_toc: true
---

# 常见问题解答（FAQ）

* TOC
{:toc}

本文档收集了使用 Fourier-GRX-HXC SDK 时常见的问题和解决方案。

## 安装问题

### 为什么安装后还需要执行 `fourier-grx install`？

DEB 包只把 ZIP 和脚本安装到系统目录。`fourier-grx install` 会把运行目录解压到 `$HOME/fourier-grx`，并完成环境准备和配置选择。

### 机型配置失败

**问题描述**：运行安装程序时输入配置选项后，提示配置错误并退出。

**解决方案**：

1. 检查输入的是选项前的 **数字**，不是文字。
2. 重新执行 `fourier-grx config` 或 `fourier-grx install`。

## 配置与运行问题

### Debug 和 Offline 有什么区别？

`debug` 面向接入真实设备的调试运行；`offline` 更适合在设备未连接时验证流程、键盘输入和基础链路。

### 配置文件路径在哪里？

默认配置文件位于：

```text
~/fourier-grx/config/hxc/config_HXC_T1_debug.yaml
~/fourier-grx/config/hxc/config_HXC_T1_offline.yaml
```

可以通过 `fourier-grx list` 查看当前实际生效的配置文件路径。

### 程序日志保存在哪里？

默认日志目录为：

```text
~/fourier-grx/log/
```

每次启动会按时间戳生成新的日志文件。

## 仓库与开发问题

### `fourier-core` 还需要单独初始化吗？

不需要。它已经作为当前仓库的普通子目录存在，不再依赖 `git submodule update --init`。

### GitHub Pages 为什么放在同一个仓库？

这样文档可以和代码、配置、打包脚本一起演进，PR 也能同时修改实现和使用说明。

### 本地预览文档失败怎么办？

确认本机已安装 Ruby / Bundler，然后执行：

```bash
bundle install
bundle exec jekyll build
```

如果是 CI 发布失败，优先检查 `.github/workflows/pages.yml` 是否已在默认分支生效。
