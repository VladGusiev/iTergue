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
    frozen_until: int = 0
    current_room: int = 0

    def __post_init__(self) -> None:
        # Not rooms[0]: rooms are numbered in scan order, which has nothing to do
        # with where anyone is standing. Level guarantees player_start is in a room,
        # so a game built from one is always right here. A Game assembled by hand can
        # stand its player anywhere, and room 0 is as good an answer as any for a
        # player who is inside a wall.
        room = self.level.room_at(self.player.position)
        self.current_room = 0 if room is None else room

    def enter_room(self, position: Point) -> None:
        """Follow the player into the room at position.

        A doorway keeps showing the room just left, because room_at is None on a
        door and there is no third room to show. Stepping off the door picks up the
        new one. This is a command, so the mover calls it and the renderer never
        asks: a query that quietly rewrote current_room would be the same mistake
        as an apply() hoisted above its guard.
        """
        room = self.level.room_at(position)
        if room is not None:
            self.current_room = room

    def take_item(self, point: Point) -> Item | None:
        return self.floor_items.pop(point, None)

    def log(self, message: str, kind: MessageKind = MessageKind.INFO) -> None:
        self.messages.append(Message(text=message, kind=kind))

    def remove_dead_enemies(self) -> None:
        self.enemies = [enemy for enemy in self.enemies if enemy.hp > 0]

    def end_turn(self) -> None:
        """Advance the clock and let enemy act. One turn one caller"""
        self.turn += 1
        # Pruning after the increment, so duration means "turns you still act
        # under it". Move it above and every buff silently lasts one turn longer.
        for ended in self.player.expire_effects(self.turn):
            self.log(f"{ended.name} wears off.")
        if self.turn < self.frozen_until:
            return  # time is stopped, so nobody else gets to move
        for enemy in self.enemies:
            if self.level.room_at(enemy.position) != self.current_room:
                continue  # a room you are not standing in is a room that is not moving
            if enemy.move(self.player, self.level):
                self.log(
                    f"The {enemy.name} attacks you for {enemy.damage} damage!",
                    kind=MessageKind.BAD,
                )
