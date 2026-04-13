from fourier_core.predefine import *


class CommProtocolDDS:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        pass

    def receive(self, data):
        # save to receive data
        self.receive_data = data

        return FunctionResult.SUCCESS

    def send(self, data):
        self.send_data = data

        return FunctionResult.SUCCESS
