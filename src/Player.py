from utils import Direction


class Player:
    x_coord: int
    y_coord: int
    display: str = "@"

    def __init__(self, x=0, y=0):
        self.y_coord = y
        self.x_coord = x

    def move(self, x: str):
        if x == Direction.UP.value:
            self.x_coord += 0
            self.y_coord += -1
        elif x == Direction.RIGHT.value:
            self.x_coord += 1
            self.y_coord += 0
        elif x == Direction.DOWN.value:
            self.x_coord += 0
            self.y_coord += 1
        elif x == Direction.LEFT.value:
            self.x_coord += -1
            self.y_coord += 0
