#!/bin/bash

set -e  # 在任意命令出错时立即退出

# 如果不存在 ~/fourier-grx 目录，则创建它
if [ ! -d ~/fourier-grx ]; then
    echo "Creating directory ~/fourier-grx..."
    mkdir -p ~/fourier-grx || {
        echo "Error: Failed to create ~/fourier-grx directory. Please check permissions."
        exit 1
    }
fi

# 如果存在 ~/fourier-grx/resource（目录或符号链接），则删除它
if [ -e ~/fourier-grx/resource ] || [ -L ~/fourier-grx/resource ]; then
    echo "Removing existing resource at ~/fourier-grx/resource..."
    rm -rf ~/fourier-grx/resource || {
        echo "Error: Failed to remove existing resource. Please check permissions."
        exit 1
    }
fi

# 将当前目录的 resource 文件夹软链接到 ~/fourier-grx/resource
ln -s "$(pwd)/resource" ~/fourier-grx/resource || {
    echo "Error: Failed to create resource link. Please check if the link already exists."
    exit 1
}

echo "Successfully created resource link at ~/fourier-grx/resource."

exit 0  # 返回成功状态码