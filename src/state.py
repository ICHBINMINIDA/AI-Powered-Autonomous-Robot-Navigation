from enum import Enum, auto


class RobotState(Enum):
    WAKE = auto()
    COMMAND = auto()
    TRACK = auto()
