# fourier-grx

## System Requirements

fourier-grx is recommended to be developed on Ubuntu 22.04, with GLIBC version 2.34 or higher.

## Quick Start

```
# 1. create conda env
conda create -n fourier-grx python=3.11

# 2. install dependencies
pip install -e .

# 3. compile and package (the packaged file will be in the dist directory)
make

# 4. install the program
sudo dpkg -i fourier-grx-x.x.x.deb
fourier-grx install

# 5. run the program
fourier-grx start
```

## Documentation

This repository now includes a GitHub Pages documentation site in the same repository:

- Site config: `_config.yaml`
- Documentation content: `docs/`
- Pages workflow: `.github/workflows/pages.yml`
