#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status

# Notice Info
echo "以下是一些运行该脚本的常见问题："
echo ""

sleep 3

# ----------------------------------------------------------------------------------------------------

# 安装依赖项
bash ./shells/dependencies.sh || {
    echo "Error: Failed to install dependencies. Please check the logs above."
    exit 1
}

echo "Successfully installed dependencies."
echo ""
sleep 1

# 创建 Resource 链接
bash ./shells/create_resource_link.sh || {
    echo "Error: Failed to create resource link. Please check the logs above."
    exit 1
}

echo "Successfully created resource link at ~/fourier-grx/resource."
echo ""
sleep 1

# 创建 Config 链接
bash ./shells/create_config_link.sh || {
    echo "Error: Failed to create config link. Please check the logs above."
    exit 1
}

echo "Successfully created config link at ~/fourier-grx/config."
echo ""
sleep 1

# 更新 Conda 环境
bash ./shells/setup_conda_env.sh || {
    echo "Error: Failed to set up conda environment. Please check the logs above."
    exit 1
}

echo "Successfully set up conda environment."
echo ""
sleep 1

echo "Congratulations! The environment has been set up successfully."
exit 0
