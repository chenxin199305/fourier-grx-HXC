---
title: 安装与启动
parent: 快速开始
nav_order: 3
---

# 安装与启动

可通过官方发布的 DEB 包直接安装 HXC 控制程序，无需自行编译。

## 下载固件

最新版本为 **v4.4.2**（HXC Blaze，linux-amd64，CPU 模式）：

```bash
wget https://fourier-grx-1302548221.cos.ap-shanghai.myqcloud.com/grx/fourier-grx-4.4.2-linux-amd64-cpu-hxc-blaze.deb
```

历史版本及完整列表请参考 [发布说明]({{ '/docs/release/' | relative_url }})。

## 安装步骤

```bash
sudo dpkg -i fourier-grx-4.4.2-linux-amd64-cpu-hxc-blaze.deb
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
