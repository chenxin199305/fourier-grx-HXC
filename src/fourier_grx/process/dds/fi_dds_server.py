import numpy
import fastdds
import msgpack

from fourier_core.predefine import *

from fourier_grx.comm import *
from fourier_grx.process.dds.fi_dds_data import (
    DDSData,
)


class DDSServer:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(DDSServer, cls).__new__(cls)

            # --------------------------------------------------

            # 构建 DDS 节点
            cls._instance.prefix = "fourier-grx"
            cls._instance.keys = ["comm", "core", "robot", "task", "grx", "rehab"]

            # 初始化通信数据模型
            cls._instance._dynalink_manager = DynalinkManager()

            # 创建 DDS Participant
            cls._instance._participant = fastdds.DomainParticipant(0)

            # 构建 Publisher 和 Subscriber
            cls._instance._publisher = cls._instance._participant.create_publisher(fastdds.PublisherQos())
            cls._instance._subscriber = cls._instance._participant.create_subscriber(fastdds.SubscriberQos())

            # 创建 Topic
            cls._instance._topic = cls._instance._participant.create_topic("fourier_dds_topic",
                                                                           "DDSData",
                                                                           fastdds.TopicQos())

            # 创建 DataWriter
            cls._instance._data_writer = cls._instance._publisher.create_datawriter(cls._instance._topic,
                                                                                    fastdds.DataWriterQos())

            # 创建 DataReader
            cls._instance._data_reader = cls._instance._subscriber.create_datareader(cls._instance._topic,
                                                                                     fastdds.DataReaderQos())

            # 设置 DataReader 的监听器
            class Listener(fastdds.DataReaderListener):
                def __init__(self, process_callback):
                    super().__init__()
                    self.process_callback = process_callback

                def on_data_available(self, reader):
                    sample = DDSData()
                    info = fastdds.SampleInfo()
                    while reader.take_next_sample(sample, info) == fastdds.RETCODE_OK:
                        if info.valid_data:
                            self.process_callback(sample)

            listener = Listener(cls._instance._process_sample)
            cls._instance._data_reader.set_listener(listener)

            # --------------------------------------------------

        return cls._instance

    def __del__(self):
        if hasattr(self, '_participant'):
            self._participant.delete_contained_entities()

    def publish(self, key=None, value=None) -> FunctionResult:
        """
        DDS 发布数据 (Server -> Client)
        """

        # 转换numpy类型
        def convert_numpy(obj):
            if isinstance(obj, numpy.generic):
                return obj.item()
            elif isinstance(obj, (dict, list, tuple)):
                return type(obj)(convert_numpy(x) for x in obj)
            return obj

        # 单key发布
        if value is not None:
            data = DDSData()
            data.key(f"{self.prefix}/dynalink_interface/{key}/server")
            data.payload(msgpack.packb(convert_numpy(value)))
            self._data_writer.write(data)
            return FunctionResult.SUCCESS

        # 全量发布
        for key in self.keys:
            dynalink_content = getattr(self._dynalink_manager, f"dynalink_{key}")
            data_dict = convert_numpy(dynalink_content.read_to_dict())

            data = DDSData()
            data.key(f"{self.prefix}/dynalink_interface/{key}/server")
            data.payload(msgpack.packb(data_dict))
            self._data_writer.write(data)

        return FunctionResult.SUCCESS

    def _process_sample(self, sample: DDSData):
        """
        处理接收到的DDS数据
        """
        key_expr = sample.key()
        payload = sample.payload()

        # 反序列化
        data_dict = msgpack.unpackb(payload)

        # 找到对应的接口
        key_map = {
            f"{self.prefix}/dynalink_interface/{key}/client":
                getattr(self._dynalink_manager, f"dynalink_{key}")
            for key in self.keys
        }

        if key_expr in key_map:
            key_map[key_expr].write_from_dict(data_dict)
