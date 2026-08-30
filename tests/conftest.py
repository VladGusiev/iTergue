import json

import pytest

from itergue.game import Game
from itergue.geometry import Point
from itergue.level import Level
from itergue.main import LEVEL_DIR
from itergue.messages import Message
from itergue.player import Player


@pytest.fixture
def game(level, player):
    return Game(level=level, player=player, enemies=[])


@pytest.fixture
def use():
    """Player.use takes a slot, so put the item in the bag and use that slot."""

    def _use(owner: Player, item, turn: int = 0) -> Message:
        owner.inventory.add(item)
        return owner.use(len(owner.inventory) - 1, turn)

    return _use


@pytest.fixture
def player():
    return Player(position=Point(5, 5))


@pytest.fixture
def level():
    return Level(LEVEL_DIR / "level-1.json")


@pytest.fixture
def write_level(tmp_path):
    def _write(data: dict) -> str:
        path = tmp_path / "level.json"
        path.write_text(json.dumps(data))
        return str(path)

    return _write
