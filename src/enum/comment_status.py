from enum import Enum


class CommentStatus(Enum):
    WAITING = 0
    NOT_REQUIRED = 1
    COMMENTED = 2
    NOT_COMMENTED = 3
    REQUIRED = 4
