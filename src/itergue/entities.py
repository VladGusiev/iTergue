from itergue.enemy import Enemy
from itergue.level import Level, LevelError
from itergue.tiles import RoomObject

ENEMY_TYPES = {
    "SLIME": {"hp": 5, "damage": 5},
    "ORC": {"hp": 20, "damage": 10},
}


def load_enemies(level: Level) -> list[Enemy]:
    enemies: list[Enemy] = []
    for enemy_data in level.enemies:
        type_enemy = enemy_data.get("type")
        try:
            display = RoomObject[type_enemy].value
            stats = ENEMY_TYPES[type_enemy]
        except KeyError as e:
            raise LevelError(f"Invalid enemy type: {type_enemy}") from e
        enemies.append(
            Enemy(
                x=enemy_data.get("x", 0),
                y=enemy_data.get("y", 0),
                display=display,
                hp=enemy_data.get("hp", stats["hp"]),
                damage=enemy_data.get("damage", stats["damage"]),
            )
        )
    return enemies
