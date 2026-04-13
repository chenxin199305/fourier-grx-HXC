---
title: 常见问题
nav_order: 4
---

# 常见问题

## 为什么安装后还需要执行 `fourier-grx install`？

DEB 包只把 ZIP 和脚本安装到系统目录。`fourier-grx install` 会把运行目录解压到 `$HOME/fourier-grx`，并完成环境准备和配置选择。

## Debug 和 Offline 有什么区别？

`debug` 面向接入真实设备的调试运行；`offline` 更适合在设备未连接时验证流程、键盘输入和基础链路。

## `fourier-core` 还需要单独初始化吗？

不需要。它已经作为当前仓库的普通子目录存在，不再依赖 `git submodule update --init`。

## GitHub Pages 为什么放在同一个仓库？

这样文档可以和代码、配置、打包脚本一起演进，PR 也能同时修改实现和使用说明。

## 本地预览文档失败怎么办？

确认本机已安装 Ruby / Bundler，然后执行：

```bash
bundle install
bundle exec jekyll build
```

如果是 CI 发布失败，优先检查 `.github/workflows/pages.yml` 是否已在默认分支生效。
