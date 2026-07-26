from enemy import Enemy
from level import Level, LevelError
from tiles import RoomObject


def load_enemies(level: Level) -> list[Enemy]:
    enemies: list[Enemy] = []
    for enemy_data in level.enemies:
        type_enemy = enemy_data.get("type")
        try:
            display = RoomObject[type_enemy].value
        except KeyError as e:
            raise LevelError(f"Invalid enemy type: {type_enemy}") from e
        enemies.append(Enemy(
            x=enemy_data.get("x", 0),
            y=enemy_data.get("y", 0),
            display=display,
            hp=enemy_data.get("hp", 10),
            damage=enemy_data.get("damage", 5),
        ))
    return enemies
