from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)

    def length(self) -> int:
        """Return the Manhattan distance from the origin."""
        return abs(self.x) + abs(self.y)


NEIGHBOURS = (Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0))
