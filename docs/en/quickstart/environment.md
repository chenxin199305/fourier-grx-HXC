---
title: Environment Setup
parent: Quick Start
nav_order: 1
---

# Environment Setup

`fourier-grx-HXC` is intended for Ubuntu 22.04 with GLIBC 2.34 or newer.

## Source-based setup

```bash
conda create -n fourier-grx python=3.11
conda activate fourier-grx
pip install -e .
cd fourier-core && pip install -e .
```

You can also use the repository helper script:

```bash
bash install_env.sh
```

It installs dependencies, creates config/resource links, and updates the Conda environment.
