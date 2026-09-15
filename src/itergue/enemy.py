from collections import deque
from dataclasses import dataclass, field

from itergue.combat import Effect, attack
from itergue.geometry import Point
from itergue.level import Level
from itergue.player import Player
from itergue.tiles import RoomObject

WALL = RoomObject.WALL.value  # caching


@dataclass
class Enemy:
    name: str = "enemy"
    position: Point = Point(0, 0)
    hp: int = 10
    damage: int = 5
    defence: int = 0
    display: str = RoomObject.SLIME.value
    # Written by nothing yet. Poison through strike is the obvious
    # next item, and the protocol is already shaped for it.
    effects: list[Effect] = field(default_factory=list)

    def move(self, player: Player, level: Level) -> bool:
        """Step one tile toward the player, or attack if already adjacent.

        Returns True if it attacked instead of moving.
        """
        # BFS to find the player's position and move towards it
        enemy_pos = self.position
        player_pos = player.position

        coordinates = deque([enemy_pos])
        path = {enemy_pos: enemy_pos}

        while coordinates:
            current_position = coordinates.popleft()
            if current_position == player_pos:
                break
            for neighbour in level.walkable_neighbours(current_position):
                if neighbour not in path:
                    path[neighbour] = current_position
                    coordinates.append(neighbour)

        if player_pos not in path:
            return False  # No path to player

        next_step = player_pos
        while path[next_step] != enemy_pos:
            next_step = path[next_step]

        if next_step == player_pos:
            # damage if the enemy is adjacent to the player
            attack(self, player)
            return True
        # move the enemy to the player's position
        self.position = next_step
        return False
