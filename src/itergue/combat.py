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


@dataclass(frozen=True, slots=True)
class Effect:
    """A bonus that stops applying once the clock passes expires_at."""

    name: str
    bonus: Stats
    expires_at: int


@runtime_checkable
class Combatant(Protocol):
    name: str
    hp: int
    position: Point
    # A bare annotation, because both fighters have to be able to gain and lose
    # effects. Affordable to add here: there are exactly two implementers and we
    # wrote both. See Lesson 22 for the widening that was not.
    effects: list[Effect]

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
