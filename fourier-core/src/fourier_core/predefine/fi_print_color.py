import sys
from enum import Enum


# Utility function to handle StrEnum compatibility
def get_str_enum():
    if sys.version_info >= (3, 11):
        from enum import StrEnum
        return StrEnum  # Python 3.11+ has StrEnum
    else:
        # Fallback for Python 3.10 and below: Create a custom StrEnum-like class
        class StrEnum(Enum):
            def __str__(self):
                return str(self.value)

        return StrEnum


# Use the utility function to get the right Enum base class
StrEnum = get_str_enum()


class PrintColor(StrEnum):
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_CYAN = "\033[96m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_RED = "\033[91m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_BLUE = "\033[94m"
