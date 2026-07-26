from enemy import Enemy
from main import _remove_dead, update_state
from player import Player


def test_remove_dead_filters_every_dead_enemy():
    # Regression: removing while iterating used to skip an enemy after a removed one.
    enemies = [Enemy(x=1, y=1, hp=0), Enemy(x=2, y=2, hp=0), Enemy(x=3, y=3, hp=5)]
    _remove_dead(enemies)
    assert [e.hp for e in enemies] == [5]


def test_bump_attack_kills_enemy_and_player_holds(player, level):
    enemies = [Enemy(x=6, y=5, hp=10)]          # directly right of player at (5, 5)
    update_state(player, ord("l"), level, enemies)
    assert enemies == []                         # killed: player dmg 10 == enemy hp 10
    assert (player.x, player.y) == (5, 5)        # attacked, did not move


def test_move_into_empty_floor(player, level):
    update_state(player, ord("l"), level, [])
    assert (player.x, player.y) == (6, 5)


def test_wall_blocks_movement(level):
    player = Player(x=1, y=1)                     # column x=0 is a wall
    update_state(player, ord("h"), level, [])
    assert (player.x, player.y) == (1, 1)
