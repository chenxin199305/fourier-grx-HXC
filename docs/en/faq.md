---
layout: default
title: FAQ
nav_order: 6
has_toc: true
nav_exclude: true
---

# FAQ

* TOC
{:toc}

This document collects common questions and solutions for the HXC branch of the Fourier-GRX-HXC SDK.

## Installation Issues

### Why do I still need `fourier-grx install` after installing the DEB?

Because the DEB installs the packaged ZIP and launcher scripts first. `fourier-grx install` expands the runtime into `$HOME/fourier-grx` and performs setup/configuration.

### Robot configuration failed

**Problem**: The installer asks for a numeric option, but reports a configuration error after input.

**Solution**:

1. Make sure you enter the option **number**, not the option text.
2. Run `fourier-grx config` or `fourier-grx install` again.

## Repository & Development Issues

### Do I still need to initialize `fourier-core` separately?

No. It now lives in this repository as a normal directory.
