import json

class Level: 
    def __init__(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
        self.width = len(data['tiles'][0])
        self.height = len(data['tiles'])
        self.player_start = data['player_start']
        self.tiles = data['tiles']
        self.enemies = data.get('enemies')

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return ' '  # Return a space for out-of-bounds coordinates