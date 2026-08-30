import dataclasses
from dataclasses import dataclass, field

from itergue.combat import Stats
from itergue.geometry import Point
from itergue.inventory import Equipment, Inventory
from itergue.items import Armor, Consumable, Cooldownable, Weapon
from itergue.messages import Message, MessageKind
from itergue.tiles import Direction, RoomObject

MOVES = {
    Direction.UP: Point(0, -1),
    Direction.RIGHT: Point(1, 0),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
}


@dataclass
class Player:
    name: str = "Kyle"
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

    def use(self, index: int, turn: int) -> Message:
        """Apply a carried item. Returns a line to log"""
        item = self.inventory[index]
        if isinstance(item, Consumable):
            if not isinstance(item, Cooldownable):
                self.inventory.take(index)  # remove it from the inventory
                return Message(item.consume(self), MessageKind.GOOD)
            if turn < item.ready_at:
                # A refusal is information, not an achievement.
                waiting = item.ready_at - turn
                return Message(
                    f"{item.name} is on cooldown for {waiting} more turns.",
                    MessageKind.INFO,
                )
            message = item.consume(self)
            # A new value, rebound into the slot. The definition is never written to
            cooling = dataclasses.replace(item, ready_at=turn + item.cooldown)
            self.inventory.replace(index, cooling)
            return Message(message, MessageKind.GOOD)
        if isinstance(item, Weapon | Armor):
            self.inventory.replace(index, self.equipment.equip(item))
            return Message(
                f"You equipped {item.name} in the {item.slot.name} slot.",
                MessageKind.GOOD,
            )
        return Message(f"You cannot use {item.name} on its own.", MessageKind.INFO)
