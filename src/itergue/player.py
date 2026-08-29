from dataclasses import dataclass, field

from itergue.combat import Stats
from itergue.geometry import Point
from itergue.items import EquipSlot, Item, Weapon
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
    base: Stats = Stats(damage=10)
    display: str = RoomObject.PLAYER.value
    equipment: dict[EquipSlot, Weapon] = field(default_factory=dict)
    inventory: list[Item] = field(default_factory=list)

    @property
    def stats(self) -> Stats:
        """Base stats plus every equipped item's bonus."""
        return sum((item.bonus for item in self.equipment.values()), self.base)

    @property
    def damage(self) -> int:
        return self.stats.damage

    def proposed_position(self, keycode: int) -> Point:
        try:
            return self.position + MOVES[Direction(keycode)]
        except ValueError:
            return self.position  # not a movement key

    def set_position(self, position: Point) -> None:
        self.position = position

    def use(self, item: Item) -> str:
        """Apply a carried item. Returns a line to log"""
        if isinstance(item, Weapon):
            displaced = self.equipment.get(EquipSlot.WEAPON)
            self.equipment[EquipSlot.WEAPON] = item
            if displaced is not None:
                self.inventory.append(displaced)  # back in the bag, not destroyed
            return f"You equipped {item.name}."
        self.hp += item.heal
        return f"You used {item.name} and healed {item.heal} HP."
