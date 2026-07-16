from player import Player
from utils import Point

def test_players_does_not_share_inventory():
    player1 = Player(x=0, y=0)
    player2 = Player(x=0, y=0)
    player1.inventory.append("sword")
    assert player1.inventory == ["sword"]
    assert player2.inventory == []

def test_proposed_position_return_point():
    player = Player(x=5, y=5)
    result = player.proposed_position(ord("l"))
    assert isinstance(result, Point)
    assert (result.x, result.y) == (6, 5)
