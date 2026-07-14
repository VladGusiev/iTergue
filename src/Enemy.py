from utils import RoomObject, attack
from Player import Player
from Level import Level
from collections import deque

class Enemy:
    x_coord: int
    y_coord: int
    hp: int
    damage: int

    def __init__(self, x=0, y=0, display=RoomObject.SLIME.value, hp=10, damage=5):
        self.y_coord = y
        self.x_coord = x
        self.display = display
        self.hp = hp
        self.damage = damage

    def move(self, player: Player, level: Level):
        # BFS to find the player's position and move towards it
        enemy_pos = (self.x_coord, self.y_coord)
        player_pos = (player.x_coord, player.y_coord)

        coordinates = deque([enemy_pos])
        path = {enemy_pos: None}

        while coordinates:
            current_position = coordinates.popleft()
            if current_position == player_pos:
                break
            current_x, current_y = current_position
            for delta_x, delta_y in ((0,1), (1,0), (0,-1), (-1,0)):
                new_position = (current_x + delta_x, current_y + delta_y)
                if new_position not in path and level.tile_at(*new_position) != RoomObject.WALL.value:
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
            self.x_coord, self.y_coord = next_step



