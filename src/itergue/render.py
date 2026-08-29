import curses
from collections import deque

from itergue.controls import CONTROLS, HELP, QUIT
from itergue.enemy import Enemy
from itergue.game import Game, Message, MessageKind
from itergue.geometry import Point
from itergue.items import EquipSlot, Item
from itergue.level import Level
from itergue.player import Player

LOG_LINES = 3
PANEL_LINES = LOG_LINES + 4  # separator, two HUD lines, and the quit line
EMPTY_SLOT = "(empty)"
FOOTER = f"Press {HELP.label} for controls, {QUIT.label.upper()} to quit"
LABEL_WIDTH = max(len(control.label) for control in CONTROLS)

MESSAGE_COLORS = {
    MessageKind.GOOD: curses.COLOR_GREEN,
    MessageKind.BAD: curses.COLOR_RED,
    MessageKind.INFO: curses.COLOR_WHITE,
}
# curses pair 0 is the terminal default and cannot be redefined, so start at 1.
COLOR_PAIRS = {kind: number for number, kind in enumerate(MESSAGE_COLORS, start=1)}


def init_colors() -> None:
    """Register one curses color pair per message kind. Call after initscr()"""
    curses.start_color()
    curses.use_default_colors()
    for kind, color in MESSAGE_COLORS.items():
        curses.init_pair(COLOR_PAIRS[kind], color, -1)


def render_messages(stdscr: curses.window, messages: deque[Message], top: int) -> None:
    for row, message in enumerate(list(messages)[-LOG_LINES:]):
        stdscr.addstr(
            top + row,
            0,
            message.text[: curses.COLS - 1],
            curses.color_pair(COLOR_PAIRS[message.kind]),
        )


def render_level(
    stdscr: curses.window, level: Level, camera: Point, height: int
) -> None:
    for point, tile in level.cells():
        screen = point - camera
        if 0 <= screen.y < height and 0 <= screen.x < curses.COLS:
            stdscr.addch(screen.y, screen.x, tile)


def render_items(
    stdscr: curses.window, items: dict[Point, Item], camera: Point, height: int
) -> None:
    for point, item in items.items():
        screen = point - camera
        if 0 <= screen.y < height and 0 <= screen.x < curses.COLS:
            stdscr.addch(screen.y, screen.x, item.display)


def render_enemies(
    stdscr: curses.window, enemies: list[Enemy], camera: Point, height: int
) -> None:
    for enemy in enemies:
        screen = enemy.position - camera
        if 0 <= screen.y < height and 0 <= screen.x < curses.COLS:
            stdscr.addch(screen.y, screen.x, enemy.display)


def render_hud(stdscr: curses.window, player: Player) -> None:
    carried = "  ".join(
        f"{number}:{item.display}{item.name}"
        for number, item in enumerate(player.inventory, start=1)
    )
    slots = []
    for slot in EquipSlot:
        item = player.equipment[slot]
        slots.append(f"{slot.value}: {item.name if item else EMPTY_SLOT}")

    stats = f"HP: {player.hp}  Damage: {player.damage}  Carried: {carried}"
    stdscr.addstr(curses.LINES - 3, 0, stats[: curses.COLS - 1])
    stdscr.addstr(curses.LINES - 2, 0, "   ".join(slots)[: curses.COLS - 1])


def render_controls(stdscr: curses.window) -> None:
    """Draw the key bindings over the whole screen. Caller waits for a keypress."""
    stdscr.clear()
    stdscr.addstr(0, 0, "Controls", curses.A_BOLD)
    for row, control in enumerate(CONTROLS, start=2):
        line = f"{control.label:<{LABEL_WIDTH}}  {control.description}"
        stdscr.addstr(row, 2, line[: curses.COLS - 3])
    stdscr.addstr(len(CONTROLS) + 3, 0, "Press any key to return")
    stdscr.refresh()


def render(stdscr: curses.window, game: Game) -> None:
    stdscr.clear()

    # The camera is the world position of the top-left map cell. Everything on the
    # map — including the player — is drawn through it, so nothing can drift apart.
    panel_top = curses.LINES - PANEL_LINES
    player = game.player
    camera = player.position - Point(curses.COLS // 2, panel_top // 2)

    render_level(stdscr, game.level, camera, panel_top)
    render_items(stdscr, game.floor_items, camera, panel_top)
    render_enemies(stdscr, game.enemies, camera, panel_top)
    screen = player.position - camera
    stdscr.addstr(screen.y, screen.x, player.display)

    render_messages(stdscr, game.messages, panel_top)
    stdscr.hline(panel_top + LOG_LINES, 0, curses.ACS_HLINE, curses.COLS)
    stdscr.addstr(curses.LINES - 1, 0, FOOTER[: curses.COLS - 1])
    render_hud(stdscr, game.player)
    stdscr.refresh()
