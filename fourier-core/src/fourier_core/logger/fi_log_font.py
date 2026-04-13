class LogFont:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    BOLD = "\033[1m"
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"

    def get_font(self, font: str = None) -> str:
        if font == "BLACK":
            return self.BLACK
        elif font == "red":
            return self.RED
        elif font == "green":
            return self.GREEN
        elif font == "yellow":
            return self.YELLOW
        elif font == "blue":
            return self.BLUE
        elif font == "magenta":
            return self.MAGENTA
        elif font == "cyan":
            return self.CYAN
        elif font == "white":
            return self.WHITE
        elif font == "bold":
            return self.BOLD
        elif font == "bold_black":
            return self.BOLD_BLACK
        elif font == "bold_red":
            return self.BOLD_RED
        elif font == "bold_green":
            return self.BOLD_GREEN
        elif font == "bold_yellow":
            return self.BOLD_YELLOW
        elif font == "bold_blue":
            return self.BOLD_BLUE
        elif font == "bold_magenta":
            return self.BOLD_MAGENTA
        elif font == "bold_cyan":
            return self.BOLD_CYAN
        elif font == "bold_white":
            return self.BOLD_WHITE
        else:
            return None

    def get_reset(self) -> str:
        return self.RESET
