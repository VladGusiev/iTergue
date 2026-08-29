import json

import pytest

from itergue.game import Game
from itergue.level import Level
from itergue.main import LEVEL_DIR
from itergue.player import Player


@pytest.fixture
def game(level, player):
    return Game(level=level, player=player, enemies=[])


@pytest.fixture
def player():
    return Player(x=5, y=5)


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
