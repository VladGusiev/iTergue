from collections import deque
from dataclasses import dataclass

from combat import attack
from level import Level
from player import Player
from tiles import RoomObject


@dataclass
class Enemy:
    x: int = 0
    y: int = 0
    hp: int = 10
    damage: int = 5
    display: str = RoomObject.SLIME.value

    def move(self, player: Player, level: Level) -> None:
        wall = RoomObject.WALL.value  # caching

        # BFS to find the player's position and move towards it
        enemy_pos = (self.x, self.y)
        player_pos = (player.x, player.y)

        coordinates = deque([enemy_pos])
        path = {enemy_pos: enemy_pos}

        while coordinates:
            current_position = coordinates.popleft()
            if current_position == player_pos:
                break
            current_x, current_y = current_position
            for delta_x, delta_y in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                new_position = (current_x + delta_x, current_y + delta_y)
                if new_position not in path and level.tile_at(*new_position) != wall:
                    coordinates.append(new_position)
                    path[new_position] = current_position

        if player_pos not in path:
            return  # No path to player

        next_step = player_pos
        while path[next_step] != enemy_pos:
            next_step = path[next_step]

        if next_step == player_pos:
            # damage if the enemy is adjacent to the player
            attack(self, player)
        else:
            # move the enemy to the player's position
            self.x, self.y = next_step
