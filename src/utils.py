from enum import Enum
from typing import NamedTuple, Protocol, runtime_checkable


@runtime_checkable
class Combatant(Protocol):
    hp: int
    damage: int

class Point(NamedTuple):
    x: int
    y: int

class Direction(Enum):
    UP = ord("k")
    RIGHT = ord("l")
    DOWN = ord("j")
    LEFT = ord("h")

class RoomObject(Enum):
    WALL = "#"
    FLOOR = "."
    PLAYER = "@"

    # enemies signs
    SLIME = "s"
    ORC = "o"

def attack(initiator: Combatant, target: Combatant) -> None:
    target.hp -= initiator.damage
    if target.hp > 0:
        initiator.hp -= target.damage

