from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol, runtime_checkable

from itergue.combat import Combatant, Stats, strike


class EquipSlot(Enum):
    """A place on the player that holds one item. The value is the UI label."""

    WEAPON = "Weapon"
    ARMOR = "Armor"


class Targeting(Enum):
    """Who an effect lands on. Closed bacause somebody has to resolve each one"""

    SELF = auto()
    NEAREST_ENEMY = auto()
    ALL_ENEMIES = auto()


@dataclass(frozen=True, slots=True)
class Armor:
    name: str
    display: str
    bonus: Stats
    description: str = ""
    slot = EquipSlot.ARMOR


@dataclass(frozen=True, slots=True)
class Weapon:
    name: str
    display: str
    bonus: Stats
    description: str = ""
    slot = EquipSlot.WEAPON


@dataclass(frozen=True, slots=True)
class Potion:
    name: str
    display: str
    heal: int
    description: str = ""
    targeting = Targeting.SELF

    def consume(self, target: Combatant) -> str:
        """Apply the item's effect to the target. Returns a line to log."""
        target.hp += self.heal
        return f"{target.name} healed by {self.name} for {self.heal} HP."


@dataclass(frozen=True, slots=True)
class AttackSpell:
    name: str
    display: str
    damage: int
    cooldown: int
    ready_at: int
    description: str = ""
    targeting = Targeting.NEAREST_ENEMY

    def consume(self, target: Combatant) -> str:
        landed = strike(self.damage, target)
        return f"{self.name} hits {target.name} for {landed} damage."


@dataclass(frozen=True, slots=True)
class HelpingSpell:
    name: str
    heal: int
    display: str
    cooldown: int
    ready_at: int
    description: str = ""
    targeting = Targeting.SELF

    def consume(self, target: Combatant) -> str:
        target.hp += self.heal
        return f"{self.name} heals {target.name} for {self.heal} HP."


@dataclass(frozen=True, slots=True)
class BuffPotion:
    name: str
    display: str
    bonus: Stats
    duration: int
    description: str = ""
    targeting = Targeting.SELF

    def consume(self, target: Combatant) -> str:
        return f"{target.name} feels the {self.name} take hold."


@dataclass(frozen=True, slots=True)
class TimeSpell:
    name: str
    display: str
    freeze: int
    cooldown: int
    ready_at: int
    description: str = ""
    targeting = Targeting.SELF

    def consume(self, target: Combatant) -> str:
        # Nothing here touches the target. The effect is on the world, so it has
        # to leave through the Outcome instead. See Freezing below.
        return f"{target.name} stops the clock."


@dataclass(frozen=True, slots=True)
class Key:
    name: str
    display: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class StoryItem:
    name: str
    display: str
    description: str = ""


# EquipSlot is a closed enum, so what can fill a slot is closed too, and a union
# buys exhaustiveness checking that a protocol cannot. The verb axis is open and
# takes the protocol instead; see Consumable below.
Equippable = Weapon | Armor
Item = (
    Equippable
    | Potion
    | Key
    | StoryItem
    | AttackSpell
    | HelpingSpell
    | BuffPotion
    | TimeSpell
)


@runtime_checkable
class Consumable(Protocol):
    """An item that does something once and is gone after use."""

    @property
    def name(self) -> str: ...
    def consume(self, target: Combatant) -> str:
        """Apply the item's effect to the target. Returns a line to log."""
        ...

    @property
    def targeting(self) -> Targeting: ...


@runtime_checkable
class Cooldownable(Protocol):
    """An item that has a cooldown before it can be used again."""

    # Properties, not bare annotations: `cooldown: int` claims a writable attribute,
    # and every item is frozen, so no real item can satisfy it.
    @property
    def cooldown(self) -> int: ...
    @property
    def ready_at(self) -> int: ...


@runtime_checkable
class Lasting(Protocol):
    """An item whose effect is still there on later turns."""

    @property
    def bonus(self) -> Stats: ...
    @property
    def duration(self) -> int: ...


@runtime_checkable
class Freezing(Protocol):
    """An item that stops the world rather than touching anybody in it."""

    @property
    def freeze(self) -> int: ...
