import json

from utils import Point

class LevelError(Exception):
    """Raised when a level file can't be loaded."""


class Level: 
    def __init__(self, path: str):
        try:
            with open(path) as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise LevelError(f"Level file not found or invalid: {path}: {e}") from e
        try:
            self.tiles = data['tiles']
            start = data['player_start']
            self.player_start = Point(start['x'], start['y'])
        except KeyError as e:
            raise LevelError(f"Missing key in level data: {e}") from e

        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        self.enemies = data.get('enemies', [])
        

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return ' '  # Return a space for out-of-bounds coordinates