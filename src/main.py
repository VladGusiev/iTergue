import curses
from curses import wrapper

from Player import Player
from Level import Level
from utils import RoomObject

from Enemy import Enemy

from typing import List


def main():
    wrapper(start)

def load_enemies(level: Level) -> List[Enemy]:
    # Load enemies from the level data
    enemies: List[Enemy] = []
    for enemy_data in level.enemies:
        enemy = Enemy(
            x=enemy_data.get("x", 0),
            y=enemy_data.get("y", 0),
            display=RoomObject[enemy_data.get("type")].value,
            hp=enemy_data.get("hp", 10),
            damage=enemy_data.get("damage", 5)
        )
        enemies.append(enemy)
    return enemies

def drawEnemies(stdscr, enemies: list, camera: dict):
    for enemy in enemies:
        sy, sx = enemy.y_coord - camera["y"], enemy.x_coord - camera["x"]
        if 0 <= sy < curses.LINES-1 and 0 <= sx < curses.COLS:
            stdscr.addch(sy, sx, enemy.display)

def drawLevel(stdscr, level: Level, camera: dict):
    for y in range(level.height):
        for x in range(level.width):
            char = level.tile_at(x, y)
            sy, sx = y - camera["y"], x - camera["x"]
            if 0 <= sy < curses.LINES-1 and 0 <= sx < curses.COLS:
                stdscr.addch(sy, sx, char)


def update_state(player: Player, camera: dict, ch: int, level: Level, enemies: List[Enemy]):
    new_x, new_y = player.proposed_position(ch) 
    # if enemy is within player's proposed position, reduce enemies hp
    for enemy in enemies:
        if enemy.x_coord == new_x and enemy.y_coord == new_y:
            enemy.hp -= player.damage
            if enemy.hp <= 0:
                enemies.remove(enemy)
            return
    # if player is within bounds of the level, update the player's position
    if level.tile_at(new_x, new_y) != RoomObject.WALL.value:
        player.set_position(new_x, new_y)

    for enemy in enemies:
        enemy.move(player, level)

    camera["x"] = player.x_coord - curses.COLS // 2
    camera["y"] = player.y_coord - curses.LINES // 2


def render(stdscr, player: Player, level: Level, camera: dict, enemies: List[Enemy]):
    stdscr.clear()

    drawLevel(stdscr, level, camera)
    drawEnemies(stdscr, enemies, camera)

    # Draw player
    stdscr.addstr(curses.LINES // 2, curses.COLS // 2, player.display)

    # Draw information
    stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
    stdscr.refresh()

def start(stdscr):
    curses.curs_set(0)  # hide cursor
    curses.start_color()

    level: Level = Level("src/levels/level-1.json")
    enemies: List[Enemy] = load_enemies(level)

    player = Player(level.player_start.get("x"), level.player_start.get("y"))
    camera = {"x": player.x_coord - curses.COLS // 2, "y": player.y_coord - curses.LINES // 2}


    render(stdscr, player, level, camera, enemies)

    index = 0
    while True:
        ch = stdscr.getch()
        if ch in (ord("Q"), ord("q")):
            break
        update_state(player, camera, ch, level, enemies)
        render(stdscr, player, level, camera, enemies)
        index += 1


if __name__ == "__main__":
    main()
