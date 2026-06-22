from utils import Direction
from utils import RoomObject

from typing import List


class Player:
    x_coord: int
    y_coord: int
    hp: int = 100
    damage: int = 10

    def __init__(self, x=0, y=0):
        self.y_coord = y
        self.x_coord = x
        self.display = RoomObject.PLAYER.value

    def proposed_position(self, keycode: str) -> List[int]:
        if keycode == Direction.UP.value:
            new_x = self.x_coord
            new_y = self.y_coord - 1
        elif keycode == Direction.RIGHT.value:
            new_x = self.x_coord + 1
            new_y = self.y_coord
        elif keycode == Direction.DOWN.value:
            new_x = self.x_coord
            new_y = self.y_coord + 1
        elif keycode == Direction.LEFT.value:
            new_x = self.x_coord - 1
            new_y = self.y_coord
        else:
            new_x = self.x_coord
            new_y = self.y_coord
        return [new_x, new_y]

    def set_position(self, x: int, y: int):
        self.x_coord = x
        self.y_coord = y
