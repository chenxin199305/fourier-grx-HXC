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

# 如果存在 ~/fourier-grx/config 目录，则删除它
if [ -d ~/fourier-grx/config ]; then
    echo "Removing existing config directory at ~/fourier-grx/config..."
    rm -rf ~/fourier-grx/config || {
        echo "Error: Failed to remove existing config directory. Please check permissions."
        exit 1
    }
fi

# 将当前目录的 config 文件夹软链接到 ~/fourier-grx/config
ln -s "$(pwd)/config" ~/fourier-grx/config || {
    echo "Error: Failed to create config link. Please check if the link already exists."
    exit 1
}

echo "Successfully created config link at ~/fourier-grx/config."

exit 0  # 返回成功状态码