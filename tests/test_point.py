from utils import Point

def test_point_is_named_tupe():
    p = Point(3, 7)
    assert p.x == 3
    assert p.y == 7
    x, y = p
    assert x == 3 and y == 7
    d = {p: "here"}
    assert d[Point(3, 7)] == "here"
    up = p._replace(y=p.y - 1)
    assert up == Point(3, 6)