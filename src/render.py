import curses

from enemy import Enemy
from geometry import Point
from level import Level
from player import Player


def render_hud(stdscr, player: Player) -> None:
    stdscr.addstr(curses.LINES - 2, 0, f"HP: {player.hp}  Damage: {player.damage}")


def render_enemies(stdscr, enemies: list[Enemy], camera: Point) -> None:
    for enemy in enemies:
        sy, sx = enemy.y - camera.y, enemy.x - camera.x
        if 0 <= sy < curses.LINES - 1 and 0 <= sx < curses.COLS:
            stdscr.addch(sy, sx, enemy.display)


def render_level(stdscr, level: Level, camera: Point) -> None:
    for y in range(level.height):
        for x in range(level.width):
            char = level.tile_at(x, y)
            sy, sx = y - camera.y, x - camera.x
            if 0 <= sy < curses.LINES - 1 and 0 <= sx < curses.COLS:
                stdscr.addch(sy, sx, char)


def render(stdscr, player: Player, level: Level, enemies: list[Enemy]) -> None:
    stdscr.clear()

    camera = Point(player.x - curses.COLS // 2, player.y - curses.LINES // 2)
    render_level(stdscr, level, camera)
    render_enemies(stdscr, enemies, camera)

    # Draw player at the centre of the viewport
    stdscr.addstr(curses.LINES // 2, curses.COLS // 2, player.display)

    render_hud(stdscr, player)
    stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
    stdscr.refresh()
