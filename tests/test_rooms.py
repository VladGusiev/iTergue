"""Rooms are discovered, not declared. These tests are what pins that."""

import pytest

from itergue.geometry import Point
from itergue.level import MAX_ROOM, Level, LevelError

# One floor split in half by a door. The door is the only thing keeping these
# two rooms apart, which is the whole reason the fill has to stop at one.
SPLIT = ["#####", "#...#", "##+##", "#...#", "#####"]
JOINED = ["#####", "#...#", "##.##", "#...#", "#####"]


def build(write_level, tiles, start=(1, 1)):
    return Level(
        write_level({"tiles": tiles, "player_start": {"x": start[0], "y": start[1]}})
    )


def test_a_door_bounds_a_room(write_level):
    # The load-bearing claim of the whole design. Let the fill run through a door
    # and every room on the floor silently becomes one room.
    assert len(build(write_level, SPLIT).rooms) == 2
    assert len(build(write_level, JOINED).rooms) == 1


def test_every_floor_tile_belongs_to_exactly_one_room(level):
    floor = {point for point, tile in level.cells() if tile == "."}
    claimed = [point for room in level.rooms for point in room.tiles]
    assert set(claimed) == floor  # every one covered
    assert len(claimed) == len(floor)  # and none of them claimed twice


def test_a_room_does_not_have_to_be_a_rectangle(level):
    # Room 0 of level 1 has a bite taken out of it, and that is deliberate: it is
    # the cheapest proof that nothing here assumes a rectangle.
    room = level.rooms[0]
    assert len(room.tiles) < (room.width - 2) * (room.height - 2)


def test_visible_carries_the_walls_that_enclose_the_room(write_level):
    room = build(write_level, SPLIT).rooms[0]
    assert Point(1, 1) in room.tiles
    assert Point(0, 0) not in room.tiles  # a corner wall is not floor
    assert Point(0, 0) in room.visible  # but it has to be drawn, or the room leaks
    assert Point(2, 2) in room.visible  # and so does the door out


def test_room_at_is_none_in_a_doorway(write_level):
    # True on every single room transition, not in some corner case, which is why
    # Game has to remember the room rather than ask for it.
    assert build(write_level, SPLIT).room_at(Point(2, 2)) is None


def test_room_at_is_none_in_a_wall(write_level):
    assert build(write_level, SPLIT).room_at(Point(0, 0)) is None


def test_a_room_too_tall_for_a_screen_is_a_level_error(write_level):
    rows = ["#...#"] * (MAX_ROOM.y + 1)
    with pytest.raises(LevelError, match="larger than"):
        build(write_level, ["#####", *rows, "#####"])


def test_a_room_that_fits_exactly_is_allowed(write_level):
    # Off-by-one guard on the cap. visible includes the walls, so the floor gets
    # two fewer rows than the cap.
    rows = ["#...#"] * (MAX_ROOM.y - 2)
    assert build(write_level, ["#####", *rows, "#####"]).rooms[0].height == MAX_ROOM.y


def test_a_player_starting_off_the_floor_is_a_level_error(write_level):
    with pytest.raises(LevelError, match="not on a floor tile"):
        build(write_level, SPLIT, start=(2, 2))  # the doorway
    with pytest.raises(LevelError, match="not on a floor tile"):
        build(write_level, SPLIT, start=(0, 0))  # a wall


def test_a_level_with_no_floor_at_all_is_a_level_error(write_level):
    with pytest.raises(LevelError, match="not on a floor tile"):
        build(write_level, ["###", "###"], start=(1, 1))


def test_level_one_is_four_rooms_and_the_player_starts_in_one(level):
    assert len(level.rooms) == 4
    assert level.room_at(level.player_start) == 0
    for room in level.rooms:
        assert room.width <= MAX_ROOM.x and room.height <= MAX_ROOM.y
