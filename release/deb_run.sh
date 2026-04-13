#!/bin/bash

# 设置环境变量
export FOURIER_GRX_HOME=$HOME/fourier-grx
export FOURIER_GRX_HOME_BAK=$HOME/fourier-grx-bak

# 判断是否有输入参数
if [ $# -eq 0 ]; then
    echo "fourier-grx 运行格式： fourier-grx [command]"
    echo ""
    echo "fourier-grx 支持以下 [command]s:"
    echo "  version : 打印版本信息"
    echo "  install : 安装 fourier-grx 控制程序"
    echo "  uninstall : 卸载 fourier-grx 控制程序"
    echo "  config : 配置 fourier-grx 运行选项"
    echo "  list : 列出 fourier-grx 当前的配置选项"
    echo "  start : 启动 fourier-grx 控制程序"
    echo "  stop : 停止已启动的 fourier-grx 控制程序"
    echo "  enable_service : 启用 fourier-grx 开机自启动"
    echo "  disable_service : 禁用 fourier-grx 开机自启动"
    echo "  background : 后台启动 fourier-grx 控制程序，防止终端意外关闭后程序停止运行。"
    echo "  setup_conda : 一键安装配套 conda 开发环境 (python 3.11)"
    echo "  setup_conda_py310 : 一键安装配套 conda 开发环境 (python 3.10)"

    exit 0
fi

# 判断是否有输入参数
if [ $# -eq 1 ]; then

    # 获取输入参数，判断是否有 version
    if [ "$1" == "version" ]; then
        # 显示版本信息
        version=$(dpkg -s fourier-grx | grep Version | awk '{print $2}')
        echo "version: $version"

        exit 0
    fi

    # 获取输入参数，判断是否有 install
    if [ "$1" == "install" ]; then
        # 拷贝 fourier-grx.zip 到 $HOME 目录
        echo "Copy fourier-grx.zip to $HOME"
        cp /usr/share/fourier-grx/fourier-grx.zip $HOME
        echo ""

        # 判断 $FOURIER_GRX_HOME 目录是否存在
        if [ -d "$FOURIER_GRX_HOME" ]; then
            # 备份 $FOURIER_GRX_HOME 目录
            echo "Backup $FOURIER_GRX_HOME to $FOURIER_GRX_HOME_BAK"

            # 删除 $FOURIER_GRX_HOME_BAK 目录
            rm -rf $FOURIER_GRX_HOME_BAK

            # 备份 $FOURIER_GRX_HOME 目录
            cp -r $FOURIER_GRX_HOME $FOURIER_GRX_HOME_BAK
        fi

        # 删除 $FOURIER_GRX_HOME 目录
        echo "Remove $FOURIER_GRX_HOME"
        rm -rf $FOURIER_GRX_HOME
        echo ""

        # 解压 fourier-grx.zip
        echo "Unzip fourier-grx.zip"
        unzip $HOME/fourier-grx.zip -d $FOURIER_GRX_HOME
        echo ""

        # 运行 setup.sh 脚本
        echo "Run setup.sh"
        bash $FOURIER_GRX_HOME/setup.sh
        echo ""

        # 运行 config.sh 脚本
        echo "Run config.sh"
        bash $FOURIER_GRX_HOME/config.sh
        echo ""

        # 删除 fourier-grx.zip
        echo "Remove fourier-grx.zip"
        rm $HOME/fourier-grx.zip
        echo ""

        # 完成 fourier-grx 安装
        echo "fourier-grx installation completed"

        exit 0
    fi

    # 获取输入参数，判断是否有 uninstall
    if [ "$1" == "uninstall" ]; then
        # 删除 $FOURIER_GRX_HOME 目录
        echo "Remove $FOURIER_GRX_HOME"
        rm -rf $FOURIER_GRX_HOME
        echo ""

        # 删除 fourier-grx.zip
        echo "Remove fourier-grx.zip"
        rm $HOME/fourier-grx.zip
        echo ""

        # 完成 fourier-grx 卸载
        echo "fourier-grx uninstallation completed"

        exit 0
    fi

    # 获取输入参数，判断是否有 config
    if [ "$1" == "config" ]; then
        # 运行 config.sh 脚本
        bash $FOURIER_GRX_HOME/config.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 list
    if [ "$1" == "list" ]; then
        # 运行 list.sh 脚本
        bash $FOURIER_GRX_HOME/list.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 start
    if [ "$1" == "start" ]; then
        # 运行 run.sh 脚本
        bash $FOURIER_GRX_HOME/run.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 stop
    if [ "$1" == "stop" ]; then
        # 杀死 fourier-grx 进程
        pkill -f fourier-grx

        exit 0
    fi

    # 获取输入参数，判断是否有 enable_service
    if [ "$1" == "enable_service" ]; then
        # 运行 setup_enable_service.sh 脚本
        bash $FOURIER_GRX_HOME/script/setup_enable_service.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 disable_service
    if [ "$1" == "disable_service" ]; then
        # 运行 setup_disable_service.sh 脚本
        bash $FOURIER_GRX_HOME/script/setup_disable_service.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 background
    if [ "$1" == "background" ]; then
        # 后台运行 run.sh 脚本
        nohup bash $FOURIER_GRX_HOME/run.sh > /dev/null 2>&1 &

        exit 0
    fi

    # 获取输入参数，判断是否有 setup_conda
    if [ "$1" == "setup_conda" ]; then
        # 运行 setup_conda_env.sh 脚本
        bash $FOURIER_GRX_HOME/script/setup_conda_env.sh

        exit 0
    fi

    # 获取输入参数，判断是否有 setup_conda_py310
    if [ "$1" == "setup_conda_py310" ]; then
        # 运行 setup_conda_env_py310.sh 脚本
        bash $FOURIER_GRX_HOME/script/setup_conda_env_py310.sh

        exit 0
    fi

    # 如果输入参数不在上述范围内，则提示错误
    echo "fourier-grx 不支持该 [command]，请使用 fourier-grx 查看支持的 [command]s。"

    exit 1

fi