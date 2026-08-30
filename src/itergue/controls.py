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
# The tenth slot is 0, as in every roguelike. Keeping the order here means the
# HUD label, the help screen and the key that acts cannot disagree.
SLOTS = "1234567890"
SLOT_INDEX = {ord(digit): index for index, digit in enumerate(SLOTS)}

SLOT = Control(
    f"{SLOTS[0]}-{SLOTS[-1]}",
    "Use or equip the item in that inventory slot",
    frozenset(SLOT_INDEX),
)
BAG = Control("i", "List what you are carrying, with names", frozenset(b"iI"))
SWAP = Control("s", "Swap your last slot for the item under you", frozenset(b"sS"))
HELP = Control("?", "Show this screen", frozenset(b"?"))
QUIT = Control("q", "Quit", frozenset(b"qQ"))

CONTROLS = (MOVE, SLOT, BAG, SWAP, HELP, QUIT)
