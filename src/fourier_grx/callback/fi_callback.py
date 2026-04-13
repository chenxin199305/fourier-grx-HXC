from fourier_core.predefine import *


class CallbackSystemExit:
    flag = FlagState.CLEAR
    shutdown = FlagState.CLEAR

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        pass
