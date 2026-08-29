from itergue.enemy import Enemy
from itergue.geometry import Point
from itergue.level import Level
from itergue.player import Player
from itergue.tiles import RoomObject

CORRIDOR = {"tiles": ["#####", "#...#", "#####"], "player_start": {"x": 1, "y": 1}}
SPLIT_ROOM = {"tiles": ["#####", "#.#.#", "#####"], "player_start": {"x": 1, "y": 1}}


def test_enemy_is_a_dataclass():
    enemy = Enemy(position=Point(1, 2), hp=10, damage=5, display=RoomObject.SLIME.value)
    assert enemy.position == Point(1, 2)
    assert enemy.hp == 10 and enemy.damage == 5
    assert enemy.display == RoomObject.SLIME.value
    assert "hp=10" in repr(enemy)
    a, b = Enemy(), Enemy()
    assert a is not b and a.hp == b.hp


def test_enemy_steps_toward_player(write_level):
    level = Level(write_level(CORRIDOR))
    player = Player(position=Point(1, 1))
    enemy = Enemy(position=Point(3, 1), damage=4)
    assert enemy.move(player, level) is False  # moved, did not attack
    assert enemy.position == Point(2, 1)
    assert player.hp == 100


def test_adjacent_enemy_attacks_instead_of_moving(write_level):
    level = Level(write_level(CORRIDOR))
    player = Player(position=Point(1, 1))
    enemy = Enemy(position=Point(2, 1), damage=4)
    assert enemy.move(player, level) is True
    assert enemy.position == Point(2, 1)  # attacked from where it stood
    assert player.hp == 96


def test_walled_off_enemy_stays_put(write_level):
    level = Level(write_level(SPLIT_ROOM))
    player = Player(position=Point(1, 1))
    enemy = Enemy(position=Point(3, 1), damage=4)
    assert enemy.move(player, level) is False  # the "no path to player" branch
    assert enemy.position == Point(3, 1)
    assert player.hp == 100
