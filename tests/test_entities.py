
from entities import load_enemies
from level import Level


def test_enemy_type_gives_default_stats(write_level):
    level = Level(write_level({"tiles": ["#"], "player_start": {"x": 0, "y": 0},
                               "enemies": [{"type": "SLIME"}]}))
    slime, = load_enemies(level)
    assert (slime.hp, slime.damage) == (5, 5)

def test_level_file_can_override_enemy_stats(write_level):
    level = Level(write_level({"tiles": ["#"], "player_start": {"x": 0, "y": 0},
                               "enemies": [{"type": "ORC", "hp": 99, "damage": 1}]}))
    orc, = load_enemies(level)
    assert (orc.hp, orc.damage) == (99, 1)

