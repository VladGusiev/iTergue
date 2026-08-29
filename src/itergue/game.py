from collections import deque
from dataclasses import dataclass, field

from itergue.enemy import Enemy
from itergue.level import Level
from itergue.player import Player

MESSAGE_LOG_SIZE = 5


@dataclass
class Game:
    level: Level
    player: Player
    enemies: list[Enemy]
    messages: deque[str] = field(default_factory=lambda: deque(maxlen=MESSAGE_LOG_SIZE))

    def log(self, message: str) -> None:
        self.messages.append(message)

    def remove_dead_enemies(self) -> None:
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
