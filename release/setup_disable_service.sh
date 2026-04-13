#!/bin/bash

# 判断是否有 $FOURIER_GRX_HOME 环境变量，如果没有则设置为 $HOME/fourier-grx
if [ -z $FOURIER_GRX_HOME ]; then
    FOURIER_GRX_HOME=$HOME/fourier-grx
fi

# Jason 2025-03-04:
# 在这里选用 crontab 来实现开机自启动，而不是使用 systemd
# 是因为我们的程序是在用户空间运行的，而不是在系统空间运行的
# 使用 crontab 可以更好地实现这一目的

echo -e " "
echo -e "\e[32m----------------------------------------------------\e[0m"
echo -e "\e[32m 为 fourier-grx 关闭开机自启动 \e[0m"
echo -e "\e[32m Disable fourier-grx auto start \e[0m"

# 获取当前的 crontab 条目
current_crontab=$(crontab -l 2>/dev/null)

# 如果 @reboot $FOURIER_GRX_HOME/run.sh 在当前的 crontab 中，则删除它
if echo "$current_crontab" | grep -q "@reboot $FOURIER_GRX_HOME/run.sh"; then
    new_crontab=$(echo "$current_crontab" | grep -v "@reboot $FOURIER_GRX_HOME/run.sh")
    echo "$new_crontab" | crontab -
fi

# change mode of the run.sh file
chmod +x $FOURIER_GRX_HOME/run.sh

# print message
echo "fourier-grx 已设置为不开机自启动"
echo "fourier-grx has been set to not auto start"
