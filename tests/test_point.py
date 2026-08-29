import dataclasses

import pytest

from itergue.geometry import Point


def test_point_holds_named_coordinates():
    p = Point(3, 7)
    assert (p.x, p.y) == (3, 7)
    assert repr(p) == "Point(x=3, y=7)"


def test_points_with_equal_coordinates_are_equal_and_hashable():
    assert Point(3, 7) == Point(3, 7)
    assert {Point(3, 7): "here"}[Point(3, 7)] == "here"  # usable as a BFS key


def test_point_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        # ty: ignore[invalid-assignment] - the assignment failing is the point
        Point(3, 7).x = 4


def test_adding_points_offsets_rather_than_concatenates():
    # Regression: as a NamedTuple this silently returned the 4-tuple (1, 2, 3, 4).
    total = Point(1, 2) + Point(3, 4)
    assert total == Point(4, 6)
    assert isinstance(total, Point)


def test_subtracting_points_gives_the_offset_between_them():
    assert Point(30, 18) - Point(10, 8) == Point(20, 10)


def test_replace_makes_a_modified_copy():
    original = Point(3, 7)
    assert dataclasses.replace(original, y=6) == Point(3, 6)
    assert original == Point(3, 7)  # unchanged
