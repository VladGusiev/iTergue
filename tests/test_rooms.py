"""Rooms are discovered, not declared. These tests are what pins that."""

import pytest

from itergue.enemy import Enemy
from itergue.game import Game
from itergue.geometry import Point
from itergue.level import MAX_ROOM, Level, LevelError
from itergue.main import update_state
from itergue.player import Player
from itergue.render import camera_for

# Level 1's three doors, and the rooms they join.
DOOR_TO_ROOM_1 = Point(13, 4)

# One floor split in half by a door. The door is the only thing keeping these
# two rooms apart, which is the whole reason the fill has to stop at one.
SPLIT = ["#####", "#...#", "##+##", "#...#", "#####"]
JOINED = ["#####", "#...#", "##.##", "#...#", "#####"]


def build(write_level, tiles, start=(1, 1)):
    return Level(
        write_level({"tiles": tiles, "player_start": {"x": start[0], "y": start[1]}})
    )


def test_a_door_bounds_a_room(write_level):
    # The load-bearing claim of the design: a fill that runs through doors makes
    # every room on the floor into one room.
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
    # True on every room transition, which is why Game remembers the room.
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


def test_a_game_starts_in_the_room_its_player_is_standing_in(level):
    # Rooms are numbered in scan order, so the starting room is whichever one holds
    # the player, and room 2 here is not room 0.
    game = Game(level=level, player=Player(position=Point(5, 11)), enemies=[])
    assert game.current_room == 2


def test_walking_through_a_door_changes_the_room(level):
    game = Game(level=level, player=Player(position=Point(12, 4)), enemies=[])
    assert game.current_room == 0
    update_state(game, ord("l"))  # onto the door
    update_state(game, ord("l"))  # and out the other side
    assert game.player.position == Point(14, 4)
    assert game.current_room == 1


def test_a_doorway_still_shows_the_room_you_are_leaving(level):
    game = Game(level=level, player=Player(position=Point(12, 4)), enemies=[])
    update_state(game, ord("l"))
    assert game.player.position == DOOR_TO_ROOM_1  # standing in the doorway
    assert level.room_at(DOOR_TO_ROOM_1) is None  # which belongs to no room
    assert game.current_room == 0  # so the room behind you is what stays on screen


def test_an_enemy_in_another_room_does_not_move(level):
    # It can path to the player: walkable_neighbours steps through doors, so
    # without the room filter this enemy walks the whole way.
    enemy = Enemy(position=Point(5, 11), hp=50)  # room 2
    game = Game(level=level, player=Player(position=Point(5, 5)), enemies=[enemy])
    assert game.current_room == 0
    game.end_turn()
    assert enemy.position == Point(5, 11)


def test_an_enemy_in_your_room_still_moves(level):
    # The control for the test above. Same call, same distance, one room.
    enemy = Enemy(position=Point(10, 2), hp=50)  # room 0, with the player
    game = Game(level=level, player=Player(position=Point(5, 5)), enemies=[enemy])
    game.end_turn()
    assert enemy.position != Point(10, 2)


def test_the_camera_centres_the_room_not_the_player(level):
    # The one piece of new arithmetic. An off-by-one here is invisible in every
    # gate and obvious the moment you look at the screen.
    room = level.rooms[0]  # 14x9
    camera = camera_for(room, Point(2, 2), 80, 17)
    on_screen = room.origin - camera
    assert on_screen == Point((80 - 14) // 2, (17 - 9) // 2)
    # The far corner lands the same distance from the other edge, give or take
    # the odd column integer division drops.
    far = Point(room.origin.x + room.width, room.origin.y + room.height) - camera
    assert 80 - far.x == on_screen.x
    assert 17 - far.y == on_screen.y


def test_a_room_wider_than_the_screen_follows_the_player_instead(level):
    # A centred room bigger than the screen leaves the player off it, and the
    # player draw is unguarded, so curses raises and the game dies.
    room, player = level.rooms[2], Point(5, 9)  # room 2 is 41 wide
    camera = camera_for(room, player, 20, 17)
    on_screen = player - camera
    assert 0 <= on_screen.x < 20  # the player is drawable, which is the whole point
    # Height still fits, so that axis is untouched and the room stays centred on it.
    assert (room.origin - camera).y == (17 - room.height) // 2
