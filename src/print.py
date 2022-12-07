from src.enum.color import Color


class Print:
    @staticmethod
    def green(text, bold=False):
        bold = Color.BOLD.value if bold else ""
        print(f"{Color.GREEN.value}{bold}{text}{Color.END_COLOR.value}")

    @staticmethod
    def red(text, bold=True):
        bold = Color.BOLD.value if bold else ""
        print(f"{Color.RED.value}{bold}{text}{Color.END_COLOR.value}")

    @staticmethod
    def blue(text, bold=False):
        bold = Color.BOLD.value if bold else ""
        print(f"{Color.BLUE.value}{bold}{text}{Color.END_COLOR.value}")

    @staticmethod
    def orange(text, bold=False):
        bold = Color.BOLD.value if bold else ""
        print(f"{Color.ORANGE.value}{bold}{text}{Color.END_COLOR.value}")

    @staticmethod
    def white(text, bold=False):
        bold = Color.BOLD.value if bold else ""
        print(f"{Color.WHITE.value}{bold}{text}{Color.END_COLOR.value}")
