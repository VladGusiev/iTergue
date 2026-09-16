import pytest

from itergue.entities import ITEM_TYPES, load_enemies, load_items
from itergue.geometry import Point
from itergue.level import Level, LevelError


def test_enemy_type_gives_default_stats(write_level):
    level = Level(
        write_level(
            {
                "tiles": ["."],
                "player_start": {"x": 0, "y": 0},
                "enemies": [{"type": "SLIME"}],
            }
        )
    )
    (slime,) = load_enemies(level)
    assert (slime.hp, slime.damage) == (5, 5)


def test_level_file_can_override_enemy_stats(write_level):
    level = Level(
        write_level(
            {
                "tiles": ["."],
                "player_start": {"x": 0, "y": 0},
                "enemies": [{"type": "ORC", "hp": 99, "damage": 1}],
            }
        )
    )
    (orc,) = load_enemies(level)
    assert (orc.hp, orc.damage) == (99, 1)


def test_load_items_keys_them_by_position(write_level):
    level = Level(
        write_level(
            {
                "tiles": ["."],
                "player_start": {"x": 0, "y": 0},
                "items": [{"type": "SMALL_HEALTH_POTION", "x": 3, "y": 4}],
            }
        )
    )
    assert load_items(level) == {Point(3, 4): ITEM_TYPES["SMALL_HEALTH_POTION"]}


def test_a_level_without_items_loads_an_empty_floor(write_level):
    level = Level(write_level({"tiles": ["."], "player_start": {"x": 0, "y": 0}}))
    assert load_items(level) == {}


def test_unknown_item_type_is_a_level_error(write_level):
    level = Level(
        write_level(
            {
                "tiles": ["."],
                "player_start": {"x": 0, "y": 0},
                "items": [{"type": "LASER", "x": 1, "y": 1}],
            }
        )
    )
    with pytest.raises(LevelError, match="LASER"):
        load_items(level)


def test_item_without_coordinates_is_a_level_error(write_level):
    # A missing coordinate must fail loudly. Defaulting it to 0 would bury
    # every item in the left-hand wall.
    level = Level(
        write_level(
            {
                "tiles": ["."],
                "player_start": {"x": 0, "y": 0},
                "items": [{"type": "DULL_SWORD"}],
            }
        )
    )
    with pytest.raises(LevelError, match="DULL_SWORD"):
        load_items(level)
