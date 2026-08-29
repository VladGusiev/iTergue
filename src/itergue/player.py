from dataclasses import dataclass, field

from itergue.combat import Stats
from itergue.geometry import Point
from itergue.inventory import Equipment, Inventory
from itergue.items import Item, Potion
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
    equipment: Equipment = field(default_factory=Equipment)
    inventory: Inventory = field(default_factory=Inventory)

    @property
    def stats(self) -> Stats:
        """Base stats plus every equipped item's bonus."""
        return self.base + self.equipment.bonus

    @property
    def damage(self) -> int:
        return self.stats.damage

    @property
    def defence(self) -> int:
        return self.stats.defence

    def proposed_position(self, keycode: int) -> Point:
        try:
            return self.position + MOVES[Direction(keycode)]
        except ValueError:
            return self.position  # not a movement key

    def set_position(self, position: Point) -> None:
        self.position = position

    def use(self, item: Item) -> str:
        """Apply a carried item. Returns a line to log"""
        if isinstance(item, Potion):
            self.hp += item.heal
            return f"You used {item.name} and healed {item.heal} HP."

        displaced = self.equipment.equip(item)
        if displaced is not None:
            # The caller just took `item` out of the bag, so there is room
            self.inventory.add(displaced)
        return f"You equipped {item.name} in the {item.slot.name} slot."
