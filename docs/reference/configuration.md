---
title: 配置文件
parent: 参考指南
nav_order: 1
---

# 配置文件

HXC 分支当前只保留两份启动配置：

- `config/hxc/config_HXC_T1_debug.yaml`
- `config/hxc/config_HXC_T1_offline.yaml`

## 关键字段

两份配置都包含以下层次：

- **Control System Layer**：调试模式、通信、DDS、记录和资源路径。
- **Robot Layer**：机器人名称、控制周期、外设开关。
- **Component Layer**：IMU、执行器通信开关。
- **Hardware Layer**：底层硬件版本。

## Debug 与 Offline 的主要差异

| 字段 | Debug | Offline |
| --- | --- | --- |
| `device_connected` | `true` | `false` |
| `peripheral.use_joystick` | `true` | `false` |
| `peripheral.use_keyboard` | `false` | `true` |
| IMU / actuator 通信 | 默认启用 | 默认关闭 |

## 运行时资源路径

配置文件中约定的默认资源目录为：

```text
~/fourier-grx/resource/hxc
~/fourier-grx/resource/zenoh
~/fourier-grx/record/hxc
```

如果你需要替换资源或记录路径，可以直接修改对应 YAML 字段。
