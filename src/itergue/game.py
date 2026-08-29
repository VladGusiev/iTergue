from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NamedTuple

from itergue.enemy import Enemy
from itergue.level import Level
from itergue.player import Player

MESSAGE_LOG_SIZE = 5


class MessageKind(Enum):
    INFO = auto()  # informational message, like where did you arrive
    BAD = auto()  # something bad happened to the player like taking damage
    GOOD = auto()  # player did something good, like killing an enemy


class Message(NamedTuple):
    text: str
    kind: MessageKind = MessageKind.INFO


@dataclass
class Game:
    level: Level
    player: Player
    enemies: list[Enemy]
    messages: deque[Message] = field(
        default_factory=lambda: deque(maxlen=MESSAGE_LOG_SIZE)
    )

    def log(self, message: str, kind: MessageKind = MessageKind.INFO) -> None:
        self.messages.append(Message(text=message, kind=kind))

    def remove_dead_enemies(self) -> None:
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
