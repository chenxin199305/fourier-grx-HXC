try:
    from fourier_core.logger import *
except ImportError:

    class Logger:
        _instance = None

        def __new__(cls):
            if not cls._instance:
                cls._instance = super().__new__(cls)

            return cls._instance

        @staticmethod
        def print_trace(message):
            print(message)

        @staticmethod
        def print_warning(message):
            print(message)

        @staticmethod
        def print_error(message):
            print(message)
