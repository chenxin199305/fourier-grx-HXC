---
layout: default
title: Packaging Flow
parent: Reference
nav_order: 4
nav_exclude: true
---

# Packaging Flow

The project is packaged as an application-first delivery:

- PyInstaller (Blaze) is the primary binary build path (~5 min end-to-end).
- `Makefile` orchestrates environment setup, binary build, ZIP packaging, and DEB packaging.
- The Jekyll documentation site is built separately for GitHub Pages and does not affect Python package outputs.
