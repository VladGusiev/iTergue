import curses
import sys
from curses import wrapper

from combat import attack
from enemy import Enemy
from entities import load_enemies
from level import Level, LevelError
from player import Player
from render import render
from tiles import RoomObject


def main() -> None:
    try:
        wrapper(start)
    except LevelError as e:
        print(f"Could not start iTergue: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def _remove_dead(enemies: list[Enemy]) -> None:
    enemies[:] = [enemy for enemy in enemies if enemy.hp > 0]


def update_state(player: Player, ch: int, level: Level, enemies: list[Enemy]) -> None:
    target = player.proposed_position(ch)

    # Bump into an enemy on the target tile → attack instead of moving.
    for enemy in enemies:
        if enemy.x == target.x and enemy.y == target.y:
            attack(player, enemy)
            _remove_dead(enemies)
            return

    # Otherwise move, unless the target tile is a wall.
    if level.tile_at(target.x, target.y) != RoomObject.WALL.value:
        player.set_position(target.x, target.y)

    # Enemies take their turn (they may die to a counter-attack).
    for enemy in list(enemies):
        enemy.move(player, level)
    _remove_dead(enemies)


def start(stdscr) -> None:
    curses.curs_set(0)  # hide cursor
    curses.start_color()

    level = Level("src/levels/level-1.json")
    enemies = load_enemies(level)
    player = Player(level.player_start.x, level.player_start.y)

    render(stdscr, player, level, enemies)
    while True:
        ch = stdscr.getch()
        if ch in (ord("Q"), ord("q")):
            break
        update_state(player, ch, level, enemies)
        render(stdscr, player, level, enemies)
        if player.hp <= 0:
            stdscr.addstr(curses.LINES // 2, curses.COLS // 2 - 5, "Game Over!")
            stdscr.refresh()
            stdscr.getch()
            break


if __name__ == "__main__":
    main()
