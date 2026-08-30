from enum import Enum, auto
from typing import NamedTuple


class MessageKind(Enum):
    INFO = auto()  # informational message, like where did you arrive
    BAD = auto()  # something bad happened to the player like taking damage
    GOOD = auto()  # player did something good, like killing an enemy


class Message(NamedTuple):
    text: str
    kind: MessageKind = MessageKind.INFO
