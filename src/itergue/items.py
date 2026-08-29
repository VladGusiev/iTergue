from dataclasses import dataclass
from enum import Enum

from itergue.combat import Stats


class EquipSlot(Enum):
    """A place on the player that holds one item. The value is the UI label."""

    WEAPON = "Weapon"
    ARMOR = "Armor"


@dataclass(frozen=True, slots=True)
class Weapon:
    name: str
    display: str
    bonus: Stats


@dataclass(frozen=True, slots=True)
class Potion:
    name: str
    display: str
    heal: int


Item = Weapon | Potion
