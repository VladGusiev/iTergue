import pytest

from player import Player

@pytest.fixture
def player():
    return Player(x=5, y=5)