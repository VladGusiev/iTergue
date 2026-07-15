from player import Player

def test_players_does_not_share_inventory():
    player1 = Player(x=0, y=0)
    player2 = Player(x=0, y=0)
    player1.inventory.append("sword")
    assert player1.inventory == ["sword"]
    assert player2.inventory == []
