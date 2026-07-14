from utils import Direction
from utils import RoomObject

from typing import List

from dataclasses import dataclass

@dataclass
class Player:
    x: int
    y: int
    hp: int = 100
    damage: int = 10
    display: str = RoomObject.PLAYER.value
    
    def proposed_position(self, keycode: str) -> List[int]:
        if keycode == Direction.UP.value:
            new_x = self.x
            new_y = self.y - 1
        elif keycode == Direction.RIGHT.value:
            new_x = self.x + 1
            new_y = self.y
        elif keycode == Direction.DOWN.value:
            new_x = self.x
            new_y = self.y + 1
        elif keycode == Direction.LEFT.value:
            new_x = self.x - 1
            new_y = self.y
        else:
            new_x = self.x
            new_y = self.y
        return [new_x, new_y]

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
