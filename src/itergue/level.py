import json
from collections.abc import Iterator
from pathlib import Path
from typing import NotRequired, TypedDict

from itergue.geometry import NEIGHBOURS, Point
from itergue.tiles import RoomObject

WALL = RoomObject.WALL.value  # caching


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
