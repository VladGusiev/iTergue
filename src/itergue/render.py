import curses
from collections import deque

from itergue.enemy import Enemy
from itergue.game import Game
from itergue.geometry import Point
from itergue.level import Level
from itergue.player import Player

LOG_LINES = 3
PANEL_LINES = LOG_LINES + 2  # +2 for the HUD and the "Press Q to quit" line


def render_level(
    stdscr: curses.window, level: Level, camera: Point, height: int
) -> None:
    for y in range(level.height):
        for x in range(level.width):
            sy, sx = y - camera.y, x - camera.x
            if 0 <= sy < height and 0 <= sx < curses.COLS:
                stdscr.addch(sy, sx, level.tile_at(x, y))


def render_enemies(
    stdscr: curses.window, enemies: list[Enemy], camera: Point, height: int
) -> None:
    for enemy in enemies:
        sy, sx = enemy.y - camera.y, enemy.x - camera.x
        if 0 <= sy < height and 0 <= sx < curses.COLS:
            stdscr.addch(sy, sx, enemy.display)


def render_messages(stdscr: curses.window, messages: deque[str]) -> None:
    top = curses.LINES - PANEL_LINES
    for row, message in enumerate(list(messages)[-LOG_LINES:]):
        stdscr.addstr(top + row, 0, message[: curses.COLS - 1])  # truncate if too long


def render_hud(stdscr: curses.window, player: Player) -> None:
    stdscr.addstr(curses.LINES - 2, 0, f"HP: {player.hp}  Damage: {player.damage}")


def render(stdscr: curses.window, game: Game) -> None:
    stdscr.clear()

    # The camera is the world position of the top-left map cell. Everything on the
    # map — including the player — is drawn through it, so nothing can drift apart.
    map_height = curses.LINES - PANEL_LINES
    player = game.player
    camera = Point(player.x - curses.COLS // 2, player.y - map_height // 2)

    render_level(stdscr, game.level, camera, map_height)
    render_enemies(stdscr, game.enemies, camera, map_height)
    stdscr.addstr(player.y - camera.y, player.x - camera.x, player.display)

    render_messages(stdscr, game.messages)
    render_hud(stdscr, game.player)
    stdscr.addstr(curses.LINES - 1, 0, "Press Q to quit")
    stdscr.refresh()
