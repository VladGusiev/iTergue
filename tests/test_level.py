import pytest

from itergue.entities import load_enemies
from itergue.level import Level, LevelError
from itergue.tiles import RoomObject


def test_missing_level_rises_levele_rror():
    with pytest.raises(LevelError):
        Level("non_existent_file.json")


def test_bad_json_rises_level_error(tmp_path):
    bad_file = tmp_path / "bad_level.json"
    bad_file.write_text("{bad json}")
    with pytest.raises(LevelError):
        Level(str(bad_file))


def test_wrong_enemy_type_rises_level_error(write_level):
    path = write_level(
        {
            "tiles": ["#"],
            "player_start": {"x": 0, "y": 0},
            "enemies": [{"type": "INVALID_TYPE"}],
        }
    )
    level = Level(str(path))
    with pytest.raises(LevelError):
        load_enemies(level)


def test_player_with_missing_start_position_rises_level_error(write_level):
    path = write_level(
        {
            "tiles": ["#"],
            "player_start": {},
        }
    )
    with pytest.raises(LevelError):
        Level(str(path))


@pytest.mark.parametrize(
    "tiles, message",
    [
        (["###", "##"], "same length"),  # ragged
        ([["#"]], "must all be strings"),  # rows are lists, not strings
        ([], "non-empty list"),  # empty
        ("###", "non-empty list"),  # a bare string, not a list
    ],
)
def test_malformed_tiles_raise_level_error(write_level, tiles, message):
    path = write_level({"tiles": tiles, "player_start": {"x": 0, "y": 0}})
    with pytest.raises(LevelError, match=message):
        Level(str(path))


def test_tile_at_treats_off_map_as_wall(level):
    assert level.tile_at(-1, 0) == RoomObject.WALL.value
    assert level.tile_at(level.width, level.height) == RoomObject.WALL.value
