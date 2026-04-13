---
title: 贡献指南
nav_order: 7
---

# 贡献指南

欢迎为 `fourier-grx-HXC` 提交代码、配置和文档改进。

## 贡献方向

- HXC 运行与打包流程修复
- `fourier-core/` 与主项目协同修改
- 配置文件、资源路径和操作文档完善
- GitHub Pages 文档内容补充

## 基本流程

1. 拉取最新代码并在功能分支上修改。
2. 同步更新相关文档页面，避免实现与说明脱节。
3. 提交 PR，说明影响范围与验证方式。

仓库根目录也提供了简要版贡献说明：`CONTRIBUTING.md`。

## 本地预览文档

```bash
bundle install
bundle exec jekyll serve --livereload
```

预览地址默认为 `http://127.0.0.1:4000/fourier-grx-HXC/`，可在提交前确认文档链接和导航是否正常。
