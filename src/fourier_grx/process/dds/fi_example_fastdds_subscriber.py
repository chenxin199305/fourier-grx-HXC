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