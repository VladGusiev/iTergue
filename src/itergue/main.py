import curses
import sys
from curses import wrapper
from pathlib import Path

from itergue.combat import attack
from itergue.controls import HELP, QUIT, SWAP
from itergue.entities import load_enemies, load_items
from itergue.game import Game, MessageKind
from itergue.geometry import Point
from itergue.level import Level, LevelError
from itergue.player import Player
from itergue.render import init_colors, render, render_controls
from itergue.tiles import RoomObject

LEVEL_DIR = Path(__file__).parent / "levels"


def main() -> None:
    try:
        wrapper(start)
    except LevelError as e:
        print(f"Could not start iTergue: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def update_state(game: Game, ch: int) -> None:
    player = game.player
    target = player.proposed_position(ch)
    slot = ch - ord("1")  # keys 1-9 use an inventory slot
    blocker = next((e for e in game.enemies if e.position == target), None)

    # Use an item from the inventory if a number key was pressed and
    # remove it from the inventory
    if 0 <= slot < len(player.inventory):
        message = player.use(player.inventory.take(slot))
        game.log(message, kind=MessageKind.GOOD)
    elif ch in SWAP.keys:
        take_from_the_floor(game, player.position)
    # Bump into an enemy on the target tile → attack instead of moving.
    elif blocker is not None:
        attack(game.player, blocker)
        game.log(
            f"You attack the {blocker.name} for {game.player.damage} damage!",
            kind=MessageKind.GOOD,
        )
        if blocker.hp <= 0:
            game.log(f"The {blocker.name} dies!", kind=MessageKind.GOOD)
        game.remove_dead_enemies()
    elif game.level.tile_at(target.x, target.y) != RoomObject.WALL.value:
        game.player.set_position(target)
        picked_up = game.take_item(target)
        if picked_up is not None:
            if player.inventory.add(picked_up):
                game.log(f"You pick up the {picked_up.name}.", kind=MessageKind.GOOD)
            else:
                game.floor_items[target] = picked_up  # no room: leave it lying there
                game.log(
                    f"You have no room for the {picked_up.name}. Press s to swap.",
                    kind=MessageKind.BAD,
                )

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
    items = load_items(level)
    player = Player(position=level.player_start)

    game_instance = Game(level=level, player=player, enemies=enemies, floor_items=items)
    game_instance.log("Your journey begins!")

    render(stdscr, game_instance)
    while True:
        ch = stdscr.getch()
        if ch in QUIT.keys:
            break
        if ch in HELP.keys:
            # Reading the controls is not a turn, so it never reaches update_state.
            render_controls(stdscr)
            stdscr.getch()
            render(stdscr, game_instance)
            continue
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


def take_from_the_floor(game: Game, position: Point) -> None:
    """Pick up what is under the player, trading the last slot if the pack is full."""
    item = game.take_item(position)
    if item is None:
        game.log("There is nothing here to pick up.", kind=MessageKind.INFO)
    elif game.player.inventory.add(item):
        game.log(f"You pick up the {item.name}.", kind=MessageKind.GOOD)
    else:
        dropped = game.player.inventory.take(-1)
        game.player.inventory.add(item)  # a slot just opened, so this holds
        game.floor_items[position] = dropped
        game.log(
            f"You swap the {dropped.name} for the {item.name}.", kind=MessageKind.INFO
        )
