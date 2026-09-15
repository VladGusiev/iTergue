import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass, field

from itergue.combat import Combatant, Effect, Stats, nearest
from itergue.geometry import Point
from itergue.inventory import Equipment, Inventory
from itergue.items import (
    Armor,
    Consumable,
    Cooldownable,
    Freezing,
    Lasting,
    Targeting,
    Weapon,
)
from itergue.messages import Message, MessageKind, Outcome, refused
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
    effects: list[Effect] = field(default_factory=list)

    @property
    def stats(self) -> Stats:
        """Base, plus every equipped item, plus whatever is still affecting you.

        No turn argument, on purpose. A Combatant.damage that needed the clock
        would stop being an int and stop satisfying the protocol.
        """
        worn = self.base + self.equipment.bonus
        # An empty generator returns the start value untouched, so no special case.
        return sum((effect.bonus for effect in self.effects), worn)

    def expire_effects(self, turn: int) -> list[Effect]:
        """Drop the effects the clock has passed. Returns the ones that ended."""
        ended = [effect for effect in self.effects if turn > effect.expires_at]
        self.effects = [effect for effect in self.effects if turn <= effect.expires_at]
        return ended

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

    def aim(
        self, targeting: Targeting, others: Sequence[Combatant]
    ) -> Combatant | None:
        """Turn a targeting rule into the combatant it lands on, if there is one."""
        if targeting is Targeting.SELF:
            return self
        return nearest(self.position, others)

    def apply(self, item: Consumable, target: Combatant, turn: int) -> str:
        """Run the item's effect now, and start the lasting part if it has one."""
        message = item.consume(target)
        if isinstance(item, Lasting):
            target.effects.append(
                Effect(item.name, item.bonus, expires_at=turn + item.duration)
            )
        return message

    def use(self, index: int, turn: int, others: Sequence[Combatant]) -> Outcome:
        """Apply a carried item. Returns a line to log"""
        item = self.inventory[index]
        if isinstance(item, Consumable):
            target = self.aim(item.targeting, others)
            if target is None:
                return refused(f"There is no target for {item.name}.")
            if isinstance(item, Cooldownable) and turn < item.ready_at:
                # A refusal is information, not an achievement.
                waiting = item.ready_at - turn
                return refused(f"{item.name} is not ready for {waiting} more turns.")
            # Every guard is above this line, because apply is a command: hoisting
            # it any higher would spend the effect on an action that then refuses.
            message = self.apply(item, target, turn)
            if isinstance(item, Cooldownable):
                # A new value, rebound into the slot. The definition is never written to
                cooling = dataclasses.replace(item, ready_at=turn + item.cooldown)
                self.inventory.replace(index, cooling)
            else:
                self.inventory.take(index)  # remove it from the inventory
            freeze = item.freeze if isinstance(item, Freezing) else 0
            return Outcome(Message(message, MessageKind.GOOD), freeze_turns=freeze)
        if isinstance(item, Weapon | Armor):
            self.inventory.replace(index, self.equipment.equip(item))
            return Outcome(
                message=Message(
                    f"You equipped {item.name} in the {item.slot.name} slot.",
                    MessageKind.GOOD,
                )
            )
        return refused(f"You cannot use {item.name} on its own.")
