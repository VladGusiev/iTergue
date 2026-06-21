from enum import Enum


class Direction(Enum):
    UP = ord("k")
    RIGHT = ord("l")
    DOWN = ord("j")
    LEFT = ord("h")

class RoomObject(Enum):
    WALL = "#"
    FLOOR = "."
    PLAYER = "@"