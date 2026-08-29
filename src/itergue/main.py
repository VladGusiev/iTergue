import curses
import sys
from curses import wrapper
from pathlib import Path

from itergue.combat import attack
from itergue.entities import load_enemies
from itergue.game import Game, MessageKind
from itergue.geometry import Point
from itergue.level import Level, LevelError
from itergue.player import Player
from itergue.render import init_colors, render
from itergue.tiles import RoomObject

LEVEL_DIR = Path(__file__).parent / "levels"


def main() -> None:
    try:
        wrapper(start)
    except LevelError as e:
        print(f"Could not start iTergue: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def update_state(game: Game, ch: int) -> None:
    target = game.player.proposed_position(ch)

    # Bump into an enemy on the target tile → attack instead of moving.
    blocker = next((e for e in game.enemies if e.position == target), None)
    if blocker is not None:
        attack(game.player, blocker)
        game.log(
            f"You attack the {blocker.name} for {game.player.damage} damage!",
            kind=MessageKind.GOOD,
        )
        if blocker.hp <= 0:
            game.log(f"The {blocker.name} dies!", kind=MessageKind.GOOD)
        game.remove_dead_enemies()
    elif game.level.tile_at(target.x, target.y) != RoomObject.WALL.value:
        game.player.set_position(Point(target))

    # Enemies always take their turn
    for enemy in game.enemies:
        if enemy.move(game.player, game.level):
            game.log(
                f"The {enemy.name} attacks you for {enemy.damage} damage!",
                kind=MessageKind.BAD,
            )


def start(stdscr: curses.window) -> None:
    curses.curs_set(0)  # hide cursor
    init_colors()  # set up color pairs for message kinds

    level = Level(LEVEL_DIR / "level-1.json")
    enemies = load_enemies(level)
    player = Player(position=level.player_start)

    game_instance = Game(level=level, player=player, enemies=enemies)
    game_instance.log("Your journey begins!")

    render(stdscr, game_instance)
    while True:
        ch = stdscr.getch()
        if ch in (ord("Q"), ord("q")):
            break
        update_state(game_instance, ch)
        render(stdscr, game_instance)
        if game_instance.player.hp <= 0:
            stdscr.addstr(
                curses.LINES // 2,
                curses.COLS // 2 - 5,
                "Game Over!",
                curses.color_pair(1),
            )
            stdscr.refresh()
            stdscr.getch()
            break
