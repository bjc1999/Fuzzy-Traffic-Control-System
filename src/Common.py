from enum import Enum


class Lane(Enum):
    left_to_right = 1
    top_to_bottom = 2
    right_to_left = 3
    bottom_to_top = 4


class TrafficStatus(Enum):
    red = 1
    green = 2
    yellow = 3


class DoubleLane(Enum):
    Horizontal = 1
    Vertical = 2


class Direction(Enum):
    forward = 1
    left = 2
    right = 3
