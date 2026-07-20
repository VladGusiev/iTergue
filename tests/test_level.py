import pytest
from level import Level, LevelError
from main import load_enemies


def test_missing_level_rises_levele_rror():
    with pytest.raises(LevelError):
        Level("non_existent_file.json")


def test_bad_json_rises_level_error(tmp_path):
    bad_file = tmp_path / "bad_level.json"
    bad_file.write_text("{bad json}")
    with pytest.raises(LevelError):
        Level(str(bad_file))

def test_wrong_enemy_type_rises_level_error(tmp_path):
    bad_file = tmp_path / "bad_level.json"
    bad_file.write_text('{"tiles": [["#"]], "player_start": {"x": 0, "y": 0}, "enemies": [{"type": "INVALID_TYPE"}]}')
    level = Level(str(bad_file))
    with pytest.raises(LevelError):
        load_enemies(level)