from typing import Protocol, runtime_checkable


@runtime_checkable
class Combatant(Protocol):
    hp: int
    damage: int


def attack(initiator: Combatant, target: Combatant) -> None:
    target.hp -= initiator.damage
