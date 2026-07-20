import json

import pytest

from player import Player

@pytest.fixture
def player():
    return Player(x=5, y=5)

@pytest.fixture
def write_level(tmp_path):
    def _write(data: dict) -> str:
        path = tmp_path / "level.json"
        path.write_text(json.dumps(data))
        return str(path)
    return _write