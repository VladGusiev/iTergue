from itergue.combat import Stats
from itergue.enemy import Enemy
from itergue.geometry import Point
from itergue.items import Armor, Item, Potion, Weapon
from itergue.level import Level, LevelError
from itergue.tiles import RoomObject

ENEMY_TYPES = {
    "SLIME": {"hp": 5, "damage": 5},
    "ORC": {"hp": 20, "damage": 10},
}

ITEM_TYPES: dict[str, Item] = {
    "SMALL_HEALTH_POTION": Potion(name="Small Health Potion", display="!", heal=20),
    "DULL_SWORD": Weapon(name="Dull Sword", display="/", bonus=Stats(damage=5)),
    "RUSTY_ARMOR": Armor(name="Rusty Armor", display="[", bonus=Stats(defence=3)),
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
                name=type_enemy.lower(),
                position=Point(enemy_data.get("x", 0), enemy_data.get("y", 0)),
                display=display,
                hp=enemy_data.get("hp", stats["hp"]),
                damage=enemy_data.get("damage", stats["damage"]),
            )
        )
    return enemies


def load_items(level: Level) -> dict[Point, Item]:
    items: dict[Point, Item] = {}
    for item_data in level.items:
        try:
            item = ITEM_TYPES[item_data["type"]]
            position = Point(item_data["x"], item_data["y"])
        except KeyError as e:
            raise LevelError(
                f"Invalid parameters for the item {item_data.get('type')}"
            ) from e
        items[position] = item
    return items
