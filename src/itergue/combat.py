from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from itergue.geometry import Point


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
    name: str
    hp: int
    position: Point

    @property
    def damage(self) -> int:
        """Read-only property that returns the damage this combatant can deal."""

    @property
    def defence(self) -> int:
        """Read-only property that returns the defence this combatant has."""


def attack(initiator: Combatant, target: Combatant) -> int:
    return strike(initiator.damage, target)


def strike(damage: int, target: Combatant) -> int:
    """Apply damage past defence. Returns what actually landed."""
    landed = max(1, damage - target.defence)
    target.hp -= landed
    return landed


def nearest(origin: Point, others: Sequence[Combatant]) -> Combatant | None:
    """Return the combatant closest to origin, or None if there are none."""
    if not others:
        return None
    return min(others, key=lambda other: (origin - other.position).length())
