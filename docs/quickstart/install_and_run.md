---
title: 安装与启动
parent: 快速开始
nav_order: 3
---

# 安装与启动

完成打包后，可通过 DEB 包把 HXC 控制程序安装到目标机器。

## 安装步骤

```bash
sudo dpkg -i fourier-grx-x.x.x.deb
fourier-grx install
```

`fourier-grx install` 会调用 `release/deb_run.sh`，并自动执行：

1. 把 `/usr/share/fourier-grx/fourier-grx.zip` 拷贝到 `$HOME`。
2. 备份旧的 `$HOME/fourier-grx` 到 `$HOME/fourier-grx-bak`。
3. 解压 ZIP 到 `$HOME/fourier-grx`。
4. 运行 `setup.sh` 完成系统准备。
5. 运行 `config.sh` 选择 HXC 变体与运行模式。

## 启动

```bash
fourier-grx start
```

实际运行时，`run.sh` 会读取：

- `robot_type="HXC"`
- `robot_version="T1"`
- `run_type="debug"` 或 `run_type="offline"`

然后拼接配置文件路径：

```text
$HOME/fourier-grx/config/hxc/config_HXC_T1_<run_type>.yaml
```

程序日志会输出到：

```text
$HOME/fourier-grx/log/<timestamp>.log
```

## 停止

```bash
fourier-grx stop
```

该命令会结束已启动的 `fourier-grx` 进程。
