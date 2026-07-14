from Enemy import Enemy
from utils import RoomObject

def test_enemy_is_a_dataclass():
    enemy = Enemy(x=1, y=2, hp=10, damage=5, display=RoomObject.SLIME.value)
    assert (enemy.x, enemy.y) == (1, 2)
    assert enemy.hp == 10 and enemy.damage == 5
    assert enemy.display == RoomObject.SLIME.value
    assert "hp=10" in repr(enemy) 
    a, b = Enemy(), Enemy()
    assert a is not b and a.hp ==b.hp