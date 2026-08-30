from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from itergue.combat import Combatant, Stats


class EquipSlot(Enum):
    """A place on the player that holds one item. The value is the UI label."""

    WEAPON = "Weapon"
    ARMOR = "Armor"


@dataclass(frozen=True, slots=True)
class Armor:
    name: str
    display: str
    bonus: Stats
    slot = EquipSlot.ARMOR


@dataclass(frozen=True, slots=True)
class Weapon:
    name: str
    display: str
    bonus: Stats
    slot = EquipSlot.WEAPON


@dataclass(frozen=True, slots=True)
class Potion:
    name: str
    display: str
    heal: int

    def consume(self, target: Combatant) -> str:
        """Apply the item's effect to the target. Returns a line to log."""
        target.hp += self.heal
        return f"{target.name} healed by {self.name} for {self.heal} HP."


@dataclass(frozen=True, slots=True)
class Spell:
    name: str
    display: str
    cooldown: int
    ready_at: int

    def consume(self, target: Combatant) -> str:
        """Apply the item's effect to the target. Returns a line to log."""
        target.hp += 10
        return f"{target.name} healed by {self.name} for 10 HP."


@dataclass(frozen=True, slots=True)
class Key:
    name: str
    display: str


@dataclass(frozen=True, slots=True)
class StoryItem:
    name: str
    display: str


# EquipSlot is a closed enum, so what can fill a slot is closed too, and a union
# buys exhaustiveness checking that a protocol cannot. The verb axis is open and
# takes the protocol instead; see Consumable below.
Equippable = Weapon | Armor
Item = Equippable | Potion | Key | StoryItem | Spell


@runtime_checkable
class Consumable(Protocol):
    """An item that does something once and is gone after use."""

    @property
    def name(self) -> str: ...
    def consume(self, target: Combatant) -> str:
        """Apply the item's effect to the target. Returns a line to log."""
        ...


@runtime_checkable
class Cooldownable(Protocol):
    """An item that has a cooldown before it can be used again."""

    # Properties, not bare annotations: `cooldown: int` claims a writable attribute,
    # and every item is frozen, so no real item can satisfy it.
    @property
    def cooldown(self) -> int: ...
    @property
    def ready_at(self) -> int: ...
