from itergue.enemy import Enemy
from itergue.geometry import Point
from itergue.main import update_state
from itergue.player import Player


def test_bump_attack_kills_enemy_and_player_holds(game):
    game.enemies = [Enemy(position=Point(6, 5), hp=10)]  # right of player at (5, 5)
    update_state(game, ord("l"))
    assert game.enemies == []  # killed: player dmg 10 == enemy hp 10
    assert game.player.position == Point(5, 5)  # attacked, did not move


def test_move_into_empty_floor(game):
    update_state(game, ord("l"))
    assert game.player.position == Point(6, 5)


def test_wall_blocks_movement(game):
    game.player = Player(position=Point(1, 1))  # column x=0 is a wall
    update_state(game, ord("h"))
    assert game.player.position == Point(1, 1)


def test_unknown_key_leaves_the_player_where_they_are(game):
    update_state(game, ord("x"))
    assert game.player.position == Point(5, 5)


def test_second_enemy_attacks_after_first_enemy_dies(game):
    game.enemies = [
        Enemy(position=Point(6, 5), hp=10, damage=3),
        Enemy(position=Point(7, 5), hp=10, damage=3),
    ]
    update_state(game, ord("l"))
    assert len(game.enemies) == 1  # first enemy killed
    assert game.player.hp == 100


def test_surviving_enemy_retaliates_once(game):
    game.enemies = [Enemy(position=Point(6, 5), hp=20, damage=3)]
    update_state(game, ord("l"))
    assert game.enemies[0].hp == 10
    assert game.player.hp == 97
