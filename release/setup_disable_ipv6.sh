#!/bin/bash

# 关闭有线网络的 ipv6 选项
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 为 fourier-grx 禁用有线网络 ipv6 \e[0m"
echo -e "\e[32m Setup disable ethernet ipv6 \e[0m"

# 获取所有有线连接的 UUID 列表
WIRED_CONNECTIONS=$(nmcli -t -f UUID,TYPE connection show | grep "ethernet" | cut -d':' -f1)

if [ -z "$WIRED_CONNECTIONS" ]; then
  echo "未找到有线网络连接！"
  exit 1
fi

# 遍历每个有线连接，禁用 IPv6
for UUID in $WIRED_CONNECTIONS; do
  echo "正在处理连接 UUID: $UUID"
  sudo nmcli connection modify "$UUID" ipv6.method "disabled"
done

# 重启 NetworkManager 使配置生效
sudo systemctl restart NetworkManager

# 短暂等待服务重启
sleep 2

# 重新激活所有有线连接（防止部分情况需手动重连）
for UUID in $WIRED_CONNECTIONS; do
  nmcli connection up "$UUID"
done

echo "所有有线连接的 IPv6 已禁用，并已重新应用配置。"
