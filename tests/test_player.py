import pytest

from itergue.geometry import Point
from itergue.player import Player


@pytest.mark.parametrize(
    "keycode, expected",
    [
        (ord("k"), Point(5, 4)),  # UP
        (ord("l"), Point(6, 5)),  # RIGHT
        (ord("j"), Point(5, 6)),  # DOWN
        (ord("h"), Point(4, 5)),  # LEFT
        (ord("x"), Point(5, 5)),  # unknown key → no move
    ],
)
def test_proposed_position_return_point(player, keycode, expected):
    result = player.proposed_position(keycode)
    assert isinstance(result, Point)
    assert result == expected


def test_proposed_position_does_not_move_the_player(player):
    player.proposed_position(ord("l"))
    assert player.position == Point(5, 5)  # it proposes, it does not commit


def test_players_does_not_share_inventory():
    player1 = Player()
    player2 = Player()
    player1.inventory.append("sword")
    assert player1.inventory == ["sword"]
    assert player2.inventory == []
