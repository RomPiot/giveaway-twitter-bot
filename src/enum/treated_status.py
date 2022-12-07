from enum import Enum


class TreatedStatus(Enum):
    NOT_TREATED = 0
    TREATED = 1
    BANNED = 2
    IGNORED = 3
    REMOVED = 4
    ERROR = 5
