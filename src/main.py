import curses
from curses import wrapper

from Player import Player
from level import Level
from utils import RoomObject


def main():
    wrapper(start)

def drawLevel(stdscr, level: Level, camera: dict):
    for y in range(level.height):
        for x in range(level.width):
            char = level.tile_at(x, y)
            sy, sx = y - camera["y"], x - camera["x"]
            if 0 <= sy < curses.LINES-1 and 0 <= sx < curses.COLS:
                stdscr.addch(sy, sx, char)


def update_state(player: Player, camera: dict, ch: int, level: Level):
    new_x, new_y = player.proposed_position(ch)
    # if player is within bounds of the level, update the player's position
    if level.tile_at(new_x, new_y) != RoomObject.WALL.value:
        player.set_position(new_x, new_y)

    camera["x"] = player.x_coord - curses.COLS // 2
    camera["y"] = player.y_coord - curses.LINES // 2


def render(stdscr, player: Player, level: Level, camera: dict):
    stdscr.clear()
    drawLevel(stdscr, level, camera)
    stdscr.addstr(curses.LINES // 2, curses.COLS // 2, player.display)
    stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
    stdscr.refresh()

def start(stdscr):
    curses.curs_set(0)  # hide cursor
    curses.start_color()

    level: Level = Level("src/levels/level-1.json")
    player = Player(level.player_start.get("x"), level.player_start.get("y"))
    camera = {"x": player.x_coord - curses.COLS // 2, "y": player.y_coord - curses.LINES // 2}


    render(stdscr, player, level, camera)

    index = 0
    while True:
        ch = stdscr.getch()
        if ch in (ord("Q"), ord("q")):
            break
        update_state(player, camera, ch, level)
        render(stdscr, player, level, camera)
        index += 1


if __name__ == "__main__":
    main()
