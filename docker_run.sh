#!/bin/bash

# 指定挂载的目录
SRC_CODE_DIR=${PWD}/..
DES_CODE_DIR=/workspace

SRC_RESOURCES_DIR=${PWD}/resource
DES_RESOURCES_DIR=/root/fourier-grx/resource

XSOCK=/tmp/.X11-unix

SRC_XAUTH=$HOME/.Xauthority
DST_XAUTH=/root/.Xauthority

SRC_INPUT=/dev/input
DST_INPUT=/dev/input

# 给 root 授权访问X服务器
xhost +local:root

read -p "是否需要使用 host 网络？（如果需要是 Docker 与宿主机之间通信，或是远端 Docker 容器通信） (y/n): " use_host_network_input
read -p "是否需要使用 bridge 网络？（如果需要是 Docker 与 Docker 容器之间通信） (y/n): " use_bridge_network_input

# 设置网络选项
if [[ "$use_host_network_input" == "y" || "$use_host_network_input" == "Y" ]]; then
  use_host_network=true
else
  use_host_network=false
fi

if [[ "$use_bridge_network_input" == "y" || "$use_bridge_network_input" == "Y" ]]; then
  use_bridge_network=true
else
  use_bridge_network=false
fi

# 创建 host 网络（如果需要是 Docker 与宿主机之间通信，或是远端 Docker 容器通信）
if [ "$use_host_network" = true ]; then
  NETWORK_NAME=host
fi

# 创建 bridge 网络（如果需要是 Docker 与 Docker 容器之间通信）
if [ "$use_bridge_network" = true ]; then
  NETWORK_NAME=inner_dds_bridge

  if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
    docker network create \
      --driver bridge \
      $NETWORK_NAME
  fi
fi

# 指定 Docker 镜像名称
IMAGE_NAME=docker.fftaicorp.com/base/aurorapy:latest
# IMAGE_NAME=aurorapy_sdk:latest
# IMAGE_NAME=fourier_grx:latest

# 运行docker容器
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v $SRC_CODE_DIR:$DES_CODE_DIR \
  -v $SRC_RESOURCES_DIR:$DES_RESOURCES_DIR \
  -v $XSOCK:$XSOCK \
  -v $SRC_XAUTH:$DST_XAUTH \
  -v $SRC_INPUT:$DST_INPUT \
  --privileged \
  --network $NETWORK_NAME \
  --ipc=host \
  "$IMAGE_NAME" bash
