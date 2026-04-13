---
layout: default
title: Packaging Flow
parent: Reference
nav_order: 4
nav_exclude: true
---

# Packaging Flow

The project is packaged as an application-first delivery:

- Nuitka is the primary binary build path.
- PyInstaller is the faster fallback path.
- `Makefile` orchestrates environment setup, wheel creation, ZIP packaging, and DEB packaging.
- The Jekyll documentation site is built separately for GitHub Pages and does not affect Python package outputs.
