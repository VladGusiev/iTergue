from collections import deque
from dataclasses import dataclass, field

from itergue.enemy import Enemy
from itergue.geometry import Point
from itergue.items import Item
from itergue.level import Level
from itergue.messages import Message, MessageKind
from itergue.player import Player

MESSAGE_LOG_SIZE = 5


@dataclass
class Game:
    level: Level
    player: Player
    enemies: list[Enemy]
    messages: deque[Message] = field(
        default_factory=lambda: deque(maxlen=MESSAGE_LOG_SIZE)
    )
    floor_items: dict[Point, Item] = field(default_factory=dict)
    turn: int = 0

    def take_item(self, point: Point) -> Item | None:
        return self.floor_items.pop(point, None)

    def log(self, message: str, kind: MessageKind = MessageKind.INFO) -> None:
        self.messages.append(Message(text=message, kind=kind))

    def remove_dead_enemies(self) -> None:
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]
