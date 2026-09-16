import curses
import sys
from curses import wrapper
from pathlib import Path

from itergue.combat import attack
from itergue.controls import BAG, HELP, MOVE, QUIT, SLOT_INDEX, SWAP
from itergue.entities import load_enemies, load_items
from itergue.game import Game
from itergue.geometry import Point
from itergue.level import Level, LevelError
from itergue.messages import MessageKind
from itergue.player import Player
from itergue.render import (
    init_colors,
    render,
    render_bag,
    render_controls,
    render_game_over,
    show_screen,
)
from itergue.tiles import RoomObject

LEVEL_DIR = Path(__file__).parent / "levels"


def build_game() -> Game:
    level = Level(LEVEL_DIR / "level-1.json")
    enemies = load_enemies(level)
    items = load_items(level)
    player = Player(position=level.player_start)

    return Game(level=level, player=player, enemies=enemies, floor_items=items)


def main() -> None:
    try:
        game = build_game()
    except LevelError as e:
        print(f"Could not start iTergue: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    game.log("Your journey begins!")
    wrapper(
        start, game
    )  # curses takes over the terminal, calls start(), and cleans up afterward


def start(stdscr: curses.window, game: Game) -> None:
    curses.curs_set(0)  # hide cursor
    init_colors()  # set up color pairs for message kinds

    render(stdscr, game)
    while True:
        ch = stdscr.getch()
        if ch in QUIT.keys:
            break
        if ch in HELP.keys:
            show_screen(stdscr, render_controls, game)
            continue  # looking at the controls is not a turn
        if ch in BAG.keys:
            show_screen(stdscr, render_bag, game)
            continue
        update_state(game, ch)
        render(stdscr, game)
        if game.player.hp <= 0:
            render_game_over(stdscr)
            break


def player_acts(game: Game, ch: int) -> bool:
    """Do what the key asks. Returns False if it asked for nothing."""
    player = game.player
    slot = SLOT_INDEX.get(ch, -1)  # -1 for every key that is not a slot key

    if 0 <= slot < len(player.inventory):
        outcome = player.use(slot, game.turn, game.enemies)
        game.log(outcome.message.text, kind=outcome.message.kind)
        game.remove_dead_enemies()
        if outcome.freeze_turns:
            # +1 because end_turn increments before it reads frozen_until.
            game.frozen_until = game.turn + outcome.freeze_turns + 1
        return outcome.spent_turn
    if ch in SWAP.keys:
        take_from_the_floor(game, player.position)
        return True
    if ch in MOVE.keys:
        return step(game, player.proposed_position(ch))
    return False


def update_state(game: Game, ch: int) -> None:
    """Apply one keypress. The enemies act only if the player spent a turn."""
    if player_acts(game, ch):
        game.end_turn()


def step(game: Game, target: Point) -> bool:
    blocker = next((e for e in game.enemies if e.position == target), None)

    if game.level.tile_at(target.x, target.y) == RoomObject.WALL.value:
        return False  # bump into a wall

    if blocker is not None:
        attack(game.player, blocker)
        game.log(
            f"You attack the {blocker.name} for {game.player.damage} damage!",
            kind=MessageKind.GOOD,
        )
        if blocker.hp <= 0:
            game.log(f"The {blocker.name} dies!", kind=MessageKind.GOOD)
        game.remove_dead_enemies()
    else:
        game.player.set_position(target)
        game.enter_room(target)
        picked_up = game.take_item(target)
        if picked_up is not None:
            if game.player.inventory.add(picked_up):
                game.log(f"You pick up the {picked_up.name}.", kind=MessageKind.GOOD)
            else:
                game.floor_items[target] = picked_up  # no room: leave it lying there
                game.log(
                    f"You have no room for the {picked_up.name}. Press s to swap.",
                    kind=MessageKind.BAD,
                )
    return True


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
