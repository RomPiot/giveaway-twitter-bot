import config
from enum import Enum


class Color(Enum):
    BLUE = '\033[94m' if config.print_in_colors else ""
    GREEN = '\033[92m' if config.print_in_colors else ""
    ORANGE = '\033[93m' if config.print_in_colors else ""
    RED = '\033[91m' if config.print_in_colors else ""
    WHITE = '\033[97m' if config.print_in_colors else ""
    HEADER = '\033[95m' if config.print_in_colors else ""
    END_COLOR = '\033[0m' if config.print_in_colors else ""
    BOLD = '\033[1m' if config.print_in_colors else ""
    UNDERLINE = '\033[4m' if config.print_in_colors else ""
