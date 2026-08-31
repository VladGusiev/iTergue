from enum import Enum, auto
from typing import NamedTuple


class MessageKind(Enum):
    INFO = auto()  # informational message, like where did you arrive
    BAD = auto()  # something bad happened to the player like taking damage
    GOOD = auto()  # player did something good, like killing an enemy


class Message(NamedTuple):
    text: str
    kind: MessageKind = MessageKind.INFO


class Outcome(NamedTuple):
    """The result of a player action, to be logged and rendered."""

    message: Message
    spent_turn: bool = True


def refused(text: str) -> Outcome:
    """Nothing happened, inform and don't spend a turn."""
    return Outcome(message=Message(text=text, kind=MessageKind.INFO), spent_turn=False)
