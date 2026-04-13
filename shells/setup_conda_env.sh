#!/bin/bash

set -e  # 在任意命令出错时立即退出

# 获取当前 conda 环境名称
CONDA_ENV_NAME=$(basename "$CONDA_PREFIX")

if [ -z "$CONDA_ENV_NAME" ]; then
    echo "Not inside a conda environment. No need to update conda environment."
    exit 0  # 返回成功状态码
fi

# 更新 GLIBC 依赖项 (确保 GLIBC 版本兼容性)
conda install -c conda-forge libstdcxx-ng -y

exit 0  # 返回成功状态码