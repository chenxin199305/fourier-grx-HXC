#!/bin/bash

# 对特定命令授予 root 权限
echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 为 fourier-grx 配置 sudo 权限 \e[0m"
echo -e "\e[32m Setup sudo permission for fourier-grx \e[0m"

user_name=$(whoami)

# edit /etc/sudoers file, add the following content:
echo " "
echo "Edit /etc/sudoers.d/$user_name file"

sudo touch /etc/sudoers.d/$user_name
echo "$user_name ALL=(ALL) NOPASSWD: /usr/bin/chmod" | sudo tee /etc/sudoers.d/$user_name
