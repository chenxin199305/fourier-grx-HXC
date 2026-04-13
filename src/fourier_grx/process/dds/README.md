# Ubuntu 22.04 use FastDDS

## 安装 FastDDS

由于我们不希望和 ROS2 耦合，所以我们选择直接从源码编译 FastDDS。

从 FastDDS 官方仓库的 package.xml 中可以了解到依赖项包括：

```xml
<!-- FastDDS package.xml -->
<build_depend>asio</build_depend>

<depend>fastcdr</depend>
<depend>foonathan_memory_vendor</depend>
<depend>libssl-dev</depend>
<depend>tinyxml2</depend>
<depend>python3</depend>

<buildtool_depend>cmake</buildtool_depend>

<doc_depend>doxygen</doc_depend>
```

1. 安装依赖 fastcdr

```shell
# 安装依赖
sudo apt update
sudo apt install cmake g++ 
sudo apt install python3-dev

# 克隆 fastcdr 仓库
git clone https://github.com/eProsima/Fast-CDR.git
cd Fast-CDR

# 编译和安装
mkdir build && cd build
cmake ..
make
sudo make install
```

2. 安装 Aiso, tinyxml2, foonathan_memory_vendor

```shell
# 安装依赖
sudo apt update
sudo apt install libasio-dev -y
sudo apt install libtinyxml2-dev
sudo apt install libfoonathan-memory-dev
```

3. 安装 FastDDS

```shell
sudo apt install cmake g++ 
sudo apt install python3-dev
git clone https://github.com/eProsima/Fast-DDS.git
cd Fast-DDS
mkdir build && cd build

cmake .. -DTHIRDPARTY=ON
# -DTHIRDPARTY=ON：自动下载和构建第三方依赖。

make
sudo make install
```

## 安装 Fast DDS Python 绑定

fastdds 并不是一个可以通过 pip 安装的 Python 包。
Fast DDS（也称为 FastRTPS）是一个 C++ 库，主要用于实现数据分发服务（DDS），
而 Python 支持是通过其 C++ 库的绑定实现的。

如果你想在 Python 中使用 Fast DDS，通常需要通过编译 Fast DDS 并生成 Python 绑定。

```shell
git clone https://github.com/eProsima/Fast-DDS-python.git

pip install -U colcon-common-extensions vcstool

# 安装依赖
sudo apt update
sudo apt install libasio-dev -y
sudo apt install libtinyxml2-dev -y
sudo apt install swig -y  # swig < 4.2
sudo apt install libpython3-dev -y

# 添加路径
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

colcon --help  # Verify colcon is now accessible

# 安装 Fast DDS Python 绑定
cd <path_to_ws>
mkdir -p fastdds_python_ws/src
cd fastdds_python_ws
wget https://raw.githubusercontent.com/eProsima/Fast-DDS-python/main/fastdds_python.repos
vcs import src < fastdds_python.repos  # 导入 Fast DDS Python 仓库代码
colcon build  # 编译 Fast DDS Python 绑定

# 引入环境变量
source install/setup.sh

# 验证 Python 绑定是否安装成功
python3
import fastdds  # 没有报错则安装成功
```

## 编写示例代码

```python
# Publisher

import fastdds
import time

# 创建 Participant
participant = fastdds.DomainParticipant(0)

# 创建 Publisher
publisher = participant.create_publisher(fastdds.PublisherQos())

# 创建 Topic
topic = participant.create_topic("ExampleTopic", "HelloWorld", fastdds.TopicQos())

# 创建 DataWriter
writer = publisher.create_datawriter(topic, fastdds.DataWriterQos())


# 定义数据类
class HelloWorld:
    def __init__(self):
        self.index = 0
        self.message = "Hello, World!"


# 创建数据实例
data = HelloWorld()

# 发布数据
for i in range(10):
    data.index = i
    print(f"Publishing: {data.message} with index {data.index}")
    writer.write(data)
    time.sleep(1)

# 清理
participant.delete_contained_entities()
fastdds.DomainParticipantFactory.get_instance().delete_participant(participant)

```

```python
# Subscriber

import fastdds

# 创建 Participant
participant = fastdds.DomainParticipant(0)

# 创建 Subscriber
subscriber = participant.create_subscriber(fastdds.SubscriberQos())

# 创建 Topic
topic = participant.create_topic("ExampleTopic", "HelloWorld", fastdds.TopicQos())

# 创建 DataReader
reader = subscriber.create_datareader(topic, fastdds.DataReaderQos())


# 定义数据类
class HelloWorld:
    def __init__(self):
        self.index = 0
        self.message = ""


# 创建数据实例
data = HelloWorld()


# 订阅数据
def on_data_available(reader):
    reader.take([data])
    print(f"Received: {data.message} with index {data.index}")


reader.set_listener(on_data_available)

# 保持运行
import time

while True:
    time.sleep(1)

# 清理
participant.delete_contained_entities()
fastdds.DomainParticipantFactory.get_instance().delete_participant(participant)
```

## 运行示例代码

你可以分别在两个终端中运行发布者和订阅者代码：

```shell
python publisher.py
```

```shell
python subscriber.py
```

## Fast DDS 数据类的限制

支持的数据类型：

- 基本类型：int, float, bool, char 等。
- 字符串：std::string（C++）或 str（Python）。
- 数组：固定大小的数组（如 int32_t array[10]）或动态数组（如 std::vector）。
- 嵌套结构体：可以在结构体中嵌套其他结构体。

不支持的数据类型：

- Python 的字典（dict）或集合（set）。
- 动态的、非固定结构的数据类型。

基于这个情况，最好的方式感觉是将 dict 通过 messagepack 序列化为二进制数据，然后通过 Fast DDS 发送。
