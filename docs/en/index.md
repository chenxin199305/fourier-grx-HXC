---
title: English Docs
nav_order: 90
has_children: true
---

# Fourier-GRX-HXC Documentation

This repository is the HXC-focused branch of `fourier-grx`. It keeps the runtime code, configuration, resources, packaging flow, and now the GitHub Pages documentation site in the same repository.

## Start here

- [Quick Start]({{ '/docs/en/quickstart/' | relative_url }})
- [Usage]({{ '/docs/en/usage/' | relative_url }})
- [Reference]({{ '/docs/en/reference/' | relative_url }})
- [FAQ]({{ '/docs/en/faq/' | relative_url }})
- [Release Notes]({{ '/docs/en/release/' | relative_url }})
- [Contributing]({{ '/docs/en/contributing/' | relative_url }})

## Scope of this branch

- HXC startup configuration lives in `config/hxc/`.
- Runtime assets for HXC live in `resource/hxc/`.
- `fourier-core/` is part of this repository as a normal subdirectory.
- GitHub Pages is built from the same repository via Actions.
