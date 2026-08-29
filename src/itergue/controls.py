from typing import NamedTuple

from itergue.tiles import Direction


class Control(NamedTuple):
    """One binding: what the help screen prints, and what actually triggers it."""

    label: str
    description: str
    keys: frozenset[int]


# frozenset(b"sS") iterates the bytes as ints, which is already what getch returns.
MOVE = Control(
    "hjkl",
    "Move left, down, up, right",
    frozenset(direction.value for direction in Direction),
)
SLOT = Control(
    "1-9",
    "Use or equip the item in that inventory slot",
    frozenset(range(ord("1"), ord("9") + 1)),
)
SWAP = Control("s", "Swap your last slot for the item under you", frozenset(b"sS"))
HELP = Control("?", "Show this screen", frozenset(b"?"))
QUIT = Control("q", "Quit", frozenset(b"qQ"))

CONTROLS = (MOVE, SLOT, SWAP, HELP, QUIT)
