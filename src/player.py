from geometry import Point
from tiles import Direction, RoomObject

from dataclasses import dataclass, field

@dataclass
class Player:
    x: int
    y: int
    hp: int = 100
    damage: int = 10
    display: str = RoomObject.PLAYER.value

    inventory: list[str] = field(default_factory=list)
    
    def proposed_position(self, keycode: int) -> Point:
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
        return Point(new_x, new_y)

    def set_position(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
