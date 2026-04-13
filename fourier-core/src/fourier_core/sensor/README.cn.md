# 传感器 （组件层）

传感器属于架构设计中的组件层，其下层连接着硬件层，上层连接着机器人层。

传感器层的主要功能是将各个不同品牌的传感器，使用相同的抽象类型 `SensorBase` 进行封装，以便于机器人层调用，而不需要关心具体的传感器品牌和接口调用顺序。

> **说明**：
> 部分厂家的传感器的接口差异较大，可能会存在一些特殊的接口调用，这种情况下，需要在传感器层进行适配，以保证机器人层的统一调用。
> 如果出现无法较好适配的传感器，可以考虑在 `SensorBase` 的基础上进行接口扩展，以适配特殊的传感器。

同时，在此层中，IO传感器，IMU传感器，无线遥控器以及其他类型的传感器，我们统称为传感器。

## 类型关系

传感器层的类型关系如下：

```mermaid
classDiagram
    class SensorBase {
        +id: int
        +init()
        +comm()
        +check()
        +upload()
    }
    class SensorIO {
    }
    class SensorFIFSE {
    }
    class SensorFDAbsEncoder {
    }
    class SensorEthernetIMU {
    }
    class SensorEthernetBISU {
    }
    class SensorEthernetWSU{
    }
    SensorBase <|-- SensorIO
    SensorBase <|-- SensorFIFSE
    SensorBase <|-- SensorFDAbsEncoder
    SensorBase <|-- SensorEthernetIMU
    SensorBase <|-- SensorEthernetBISU
    SensorBase <|-- SensorEthernetWSU
```

> **说明**：
> 这里的图形需要使用支持 `mermaid` 的 Markdown 编辑器才能正常显示。

## 接口说明

关节层的接口说明如下：

- `upload()`：上传传感器的状态参数，该方法会从硬件层读取电机的**状态参数**，并将其上传到传感器层。数据传输会经过**传感器层**，**硬件层**。
- `download()`：下载传感器的控制参数，该方法会将传感器的**控制参数**下载到硬件层，以便硬件层控制电机。数据传输会经过**传感器层**，**硬件层**。

```mermaid
sequenceDiagram
    participant SensorLayer
    participant HardwareLayer
    
    HardwareLayer ->> SensorLayer: upload()
    SensorLayer ->> HardwareLayer: download()
```