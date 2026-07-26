from enemy import Enemy
from tiles import RoomObject
from level import Level
from player import Player


def test_enemy_is_a_dataclass():
    enemy = Enemy(x=1, y=2, hp=10, damage=5, display=RoomObject.SLIME.value)
    assert (enemy.x, enemy.y) == (1, 2)
    assert enemy.hp == 10 and enemy.damage == 5
    assert enemy.display == RoomObject.SLIME.value
    assert "hp=10" in repr(enemy)
    a, b = Enemy(), Enemy()
    assert a is not b and a.hp == b.hp

def test_enemy_steps_toward_player(write_level):
    level = Level(write_level({"tiles": ["#####", "#...#", "#####"],
                               "player_start": {"x": 1, "y": 1}}))
    player, enemy = Player(x=1, y=1), Enemy(x=3, y=1, damage=4)
    enemy.move(player, level)
    assert (enemy.x, enemy.y) == (2, 1)
    assert player.hp == 100          # moved, did not attack

def test_adjacent_enemy_attacks_instead_of_moving(write_level):
    level = Level(write_level({"tiles": ["#####", "#...#", "#####"],
                               "player_start": {"x": 1, "y": 1}}))
    player, enemy = Player(x=1, y=1), Enemy(x=2, y=1, damage=4)
    enemy.move(player, level)
    assert (enemy.x, enemy.y) == (2, 1)
    assert player.hp == 96

def test_walled_off_enemy_stays_put(write_level):
    level = Level(write_level({"tiles": ["#####", "#.#.#", "#####"],
                               "player_start": {"x": 1, "y": 1}}))
    player, enemy = Player(x=1, y=1), Enemy(x=3, y=1, damage=4)
    enemy.move(player, level)
    assert (enemy.x, enemy.y) == (3, 1)
    assert player.hp == 100          # the `player_pos not in path` branch

