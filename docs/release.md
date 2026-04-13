---
title: 发布说明
nav_order: 5
---

# 发布说明

仓库当前包含两类发布产物：

## 1. GitHub Pages 文档站

Pages 由 `.github/workflows/pages.yml` 发布：

- 推送到默认分支时自动构建。
- 也支持 `workflow_dispatch` 手动触发。
- 使用 `actions/jekyll-build-pages` 构建 `_site`。
- 使用 `actions/deploy-pages` 部署到 GitHub Pages。

第一次启用时，需要在仓库设置中把 **Pages Source** 配置为 **GitHub Actions**。

## 2. HXC 运行产物

代码交付产物仍由 `Makefile` 负责：

- `dist/*.deb`
- `dist/*.zip`
- `dist/fourier_grx-*.whl`
- `fourier-core/dist/fourier_core-*.whl`

建议将 Pages 文档发布和二进制发布视为两条独立流程，互不阻塞。
