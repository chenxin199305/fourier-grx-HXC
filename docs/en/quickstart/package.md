---
layout: default
title: Build and Package
parent: Quick Start
nav_order: 2
nav_exclude: true
---

# Build and Package

The root `Makefile` provides the main delivery paths for the HXC branch.

| Command | Purpose | Output |
| --- | --- | --- |
| `make` / `make blaze` | Blaze build (~5 min) | `dist/*-blaze.deb`, `dist/*.zip` |
| `make test` | Test build, skips zip rename | `dist/*-blaze.deb` |
| `make build` | Build the Python wheel | `dist/fourier_grx-*.whl` |
| `make clean_all` | Clean project and `fourier-core` artifacts | clears `build/`, `dist/` |

The build flow installs `fourier-grx` and `fourier-core` in editable mode, builds the binary with PyInstaller, then assembles ZIP and DEB artifacts.
