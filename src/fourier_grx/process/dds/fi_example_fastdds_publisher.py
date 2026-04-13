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
