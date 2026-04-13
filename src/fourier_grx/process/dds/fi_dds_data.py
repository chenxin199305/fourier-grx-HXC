class DDSData:
    """
    fourier-grx DDS 数据结构:
    module Fourier {
        module DDS {
            struct Data {
                string key;
                str payload;
            };
        };
    };
    """

    def __init__(self):
        self.key = ""
        self.payload = ""  # 用 msgpack 编码后的数据
