---
title: Build and Package
parent: Quick Start
nav_order: 2
---

# Build and Package

The root `Makefile` provides the main delivery paths for the HXC branch.

| Command | Purpose |
| --- | --- |
| `make` | Full Nuitka-based package build |
| `make fast` | Faster PyInstaller-based package build |
| `make test` | Fastest testing-oriented package build |
| `make build` | Build the Python wheel |

The build flow installs both `fourier-grx` and `fourier-core`, builds wheels, creates the binary, then assembles ZIP and DEB artifacts.
