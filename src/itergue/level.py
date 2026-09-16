import json
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, TypedDict

from itergue.geometry import AROUND, NEIGHBOURS, Point
from itergue.tiles import RoomObject

WALL = RoomObject.WALL.value  # caching
FLOOR = RoomObject.FLOOR.value

# The biggest room a screen can hold: 80 columns, and 24 rows less the seven-line
# panel. Fixed on purpose. Read it from curses.COLS instead and the same seed would
# build a different dungeon on a different terminal.
MAX_ROOM = Point(80, 17)


@dataclass(frozen=True, slots=True)
class Room:
    """One enclosed region of floor, and the walls and doors that enclose it.

    Any shape, because it is discovered rather than declared.
    """

    tiles: frozenset[Point]  # the floor you can stand on
    visible: frozenset[Point]  # that floor plus everything around it, so walls draw
    origin: Point  # top-left of visible, in world coordinates
    width: int
    height: int


class EnemySpecification(TypedDict):
    type: str
    x: NotRequired[int]
    y: NotRequired[int]
    hp: NotRequired[int]
    damage: NotRequired[int]


class ItemSpecification(TypedDict):
    type: str
    x: int
    y: int


class LevelError(Exception):
    """Raised when a level file can't be loaded."""


class Level:
    def __init__(self, path: str | Path):
        try:
            with open(path) as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise LevelError(f"Level file not found or invalid: {path}: {e}") from e
        try:
            self.tiles: list[str] = data["tiles"]
            start = data["player_start"]
            self.player_start = Point(start["x"], start["y"])
        except KeyError as e:
            raise LevelError(f"Missing key in level data: {e}") from e

        if not isinstance(self.tiles, list) or not self.tiles:
            raise LevelError("Level tiles must be a non-empty list.")
        if not all(isinstance(row, str) for row in self.tiles):
            raise LevelError("Level tiles rows must all be strings.")

        self.width = len(self.tiles[0])
        self.height = len(self.tiles)

        if any(len(row) != self.width for row in self.tiles):
            raise LevelError("All rows in level tiles must be the same length.")

        self.enemies: list[EnemySpecification] = data.get("enemies", [])
        self.items: list[ItemSpecification] = data.get("items", [])

        self.rooms = self._discover_rooms()
        self._room_of: dict[Point, int] = {
            point: index
            for index, room in enumerate(self.rooms)
            for point in room.tiles
        }
        for index, room in enumerate(self.rooms):
            if room.width > MAX_ROOM.x or room.height > MAX_ROOM.y:
                raise LevelError(
                    f"Room {index} is {room.width}x{room.height}, larger than the "
                    f"{MAX_ROOM.x}x{MAX_ROOM.y} one screen can hold."
                )
        # Parse, don't validate: past this line a level always has a room to start
        # in, so nothing downstream has to ask what happens when it doesn't.
        if self.room_at(self.player_start) is None:
            raise LevelError(
                f"player_start {self.player_start} is not on a floor tile."
            )

    def _discover_rooms(self) -> list[Room]:
        """Every enclosed region of floor, found by flood fill.

        Only FLOOR is filled through, so walls, doors and anything unrecognised all
        bound a room. Rooms are discovered and never declared, which is what lets
        them be any shape: a generator only has to carve, never to write down what
        it carved.
        """
        rooms: list[Room] = []
        seen: set[Point] = set()
        for start, tile in self.cells():
            if tile != FLOOR or start in seen:
                continue
            tiles = {start}
            seen.add(start)
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for delta in NEIGHBOURS:
                    neighbour = current + delta
                    # tile_at reports off-map as wall, so the edges need no case.
                    if (
                        neighbour in seen
                        or self.tile_at(neighbour.x, neighbour.y) != FLOOR
                    ):
                        continue
                    seen.add(neighbour)
                    tiles.add(neighbour)
                    queue.append(neighbour)
            visible = tiles | {tile + delta for tile in tiles for delta in AROUND}
            origin = Point(min(p.x for p in visible), min(p.y for p in visible))
            rooms.append(
                Room(
                    tiles=frozenset(tiles),
                    visible=frozenset(visible),
                    origin=origin,
                    width=max(p.x for p in visible) - origin.x + 1,
                    height=max(p.y for p in visible) - origin.y + 1,
                )
            )
        return rooms

    def room_at(self, point: Point) -> int | None:
        """Which room contains point. None on a wall, and None in a doorway."""
        return self._room_of.get(point)

    def cells(self) -> Iterator[tuple[Point, str]]:
        """Every tile in the level, as (position, character)"""
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                yield Point(x, y), tile

    def walkable_neighbours(self, point: Point) -> Iterator[Point]:
        """The four orthogonal neighbours of point that are not walls"""
        for delta in NEIGHBOURS:
            neighbour = point + delta
            if self.tile_at(neighbour.x, neighbour.y) != WALL:
                yield neighbour

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return WALL
