#!/bin/bash

# 设置有线网络的 ipv4 地址
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 为 fourier-grx 配置有线网络静态 ipv4 \e[0m"
echo -e "\e[32m Setup ethernet ipv4 static ip \e[0m"

# 配置参数
IPV4_ADDRESS="192.168.137.220/24"
GATEWAY="192.168.137.1"       # 根据实际网络修改网关
DNS_SERVERS="8.8.8.8,8.8.4.4" # 根据需求修改 DNS

# 获取第一个有线连接的 UUID
WIRED_UUID=$(nmcli -t -f UUID,TYPE connection show | grep "ethernet" | head -n1 | cut -d':' -f1)

if [ -z "$WIRED_UUID" ]; then
  echo "未找到有线网络连接！"
  exit 1
fi

# 配置静态 IPv4 地址
sudo nmcli connection modify "$WIRED_UUID" \
  ipv4.method manual \
  ipv4.addresses "$IPV4_ADDRESS" \
  ipv4.gateway "$GATEWAY" \
  ipv4.dns "$DNS_SERVERS"

# 重新激活连接以应用配置
sudo nmcli connection down "$WIRED_UUID"
sudo nmcli connection up "$WIRED_UUID"

echo "有线网络已配置静态 IPv4 地址：$IPV4_ADDRESS"
