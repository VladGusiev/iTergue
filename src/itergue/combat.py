from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Stats:
    damage: int = 0
    defence: int = 0

    def __add__(self, other: Stats) -> Stats:
        return Stats(
            damage=self.damage + other.damage,
            defence=self.defence + other.defence,
        )


@runtime_checkable
class Combatant(Protocol):
    hp: int

    @property
    def damage(self) -> int:
        """Read-only property that returns the damage this combatant can deal."""


def attack(initiator: Combatant, target: Combatant) -> None:
    target.hp -= initiator.damage
