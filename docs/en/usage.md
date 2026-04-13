---
layout: default
title: Usage
nav_order: 5
has_toc: true
nav_exclude: true
---

# Usage

* TOC
{:toc}

This document describes the most common operational flows for the Fourier-GRX-HXC SDK.

## Selecting the runtime configuration

`fourier-grx config` currently provides two HXC variants:

- `HXC T1 Debug`
- `HXC T1 Offline`

## Viewing the current configuration

```bash
fourier-grx list
```

## Starting the program

```bash
fourier-grx start
```

## Running in background

```bash
fourier-grx background
```

## Auto-start on boot

```bash
fourier-grx enable_service
fourier-grx disable_service
```

## Conda environment helpers

- `fourier-grx config`
- `fourier-grx setup_conda`
- `fourier-grx setup_conda_py310`
