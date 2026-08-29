from dataclasses import dataclass, field

from itergue.geometry import Point
from itergue.tiles import Direction, RoomObject

MOVES = {
    Direction.UP: Point(0, -1),
    Direction.RIGHT: Point(1, 0),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
}


@dataclass
class Player:
    position: Point = Point(0, 0)
    hp: int = 100
    damage: int = 10
    display: str = RoomObject.PLAYER.value

    inventory: list[str] = field(default_factory=list)

    def proposed_position(self, keycode: int) -> Point:
        try:
            return self.position + MOVES[Direction(keycode)]
        except ValueError:
            return self.position  # not a movement key

    def set_position(self, position: Point) -> None:
        self.position = position
