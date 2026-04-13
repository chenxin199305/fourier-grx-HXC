---
layout: default
title: 发布说明
nav_order: 7
has_toc: true
---

# 发布说明

* TOC
{:toc}

## 正式版本

当前仓库主要维护两类正式发布内容：文档站发布与运行产物发布。

### GitHub Pages 文档站

Pages 由 `.github/workflows/pages.yml` 发布：

- 推送到默认分支时自动构建。
- 也支持 `workflow_dispatch` 手动触发。
- 使用 `actions/jekyll-build-pages` 构建 `_site`。
- 使用 `actions/deploy-pages` 部署到 GitHub Pages。

第一次启用时，需要在仓库设置中把 **Pages Source** 配置为 **GitHub Actions**。

### HXC 运行产物

代码交付产物仍由 `Makefile` 负责：

- `dist/*.deb`
- `dist/*.zip`
- `dist/fourier_grx-*.whl`
- `fourier-core/dist/fourier_core-*.whl`

## 预览版本

预览版本指尚未正式发布的内容，可能包含新的文档调整或打包改动，但不保证稳定性。

当前暂无单独维护的预览版本列表。

## 安装方法

运行产物安装流程请参考 [快速开始]({{ '/docs/quickstart/install_and_run/' | relative_url }})。

## 发布说明

### GitHub Pages

文档站与代码共存于同一仓库，默认发布地址为：

```text
https://chenxin199305.github.io/fourier-grx-HXC/
```

### 运行包

建议将 Pages 文档发布和二进制发布视为两条独立流程，互不阻塞。
