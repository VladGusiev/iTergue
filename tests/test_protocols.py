from itergue.combat import Combatant, Stats, attack
from itergue.enemy import Enemy
from itergue.items import Weapon
from itergue.player import Player


def test_player_and_enemy_are_combatants():
    # Combatant only asks for hp and a readable damage. Player derives damage
    # from a property, Enemy stores it in a plain field, and a read-only
    # protocol member accepts both.
    assert isinstance(Player(), Combatant)
    assert isinstance(Enemy(), Combatant)


def test_attack_leaves_the_initiator_untouched():
    hero = Player(hp=20, base=Stats(damage=5))
    monster = Enemy(hp=15, damage=3)
    attack(hero, monster)
    assert monster.hp == 10  # 15 - 5
    assert hero.hp == 20


def test_attack_uses_the_initiators_equipment(player):
    # attack reads Player.damage, which is base + whatever is wielded.
    monster = Enemy(hp=50, damage=3)
    player.use(Weapon(name="axe", display="/", bonus=Stats(damage=15)))
    attack(player, monster)
    assert monster.hp == 25  # 50 - (10 base + 15 axe)


def test_defence_subtracts_from_the_hit():
    hero = Player(hp=20, base=Stats(damage=5))
    monster = Enemy(hp=15, damage=3)
    attack(monster, hero)
    assert hero.hp == 20 - 3  # no armour worn, so nothing is soaked


def test_worn_armour_soaks_part_of_the_hit(player):
    from itergue.items import Armor

    player.use(Armor(name="plate", display="[", bonus=Stats(defence=2)))
    attack(Enemy(hp=15, damage=5), player)
    assert player.hp == 97  # 100 - (5 - 2)


def test_a_hit_always_lands_for_at_least_one():
    from itergue.items import Armor

    hero = Player(hp=100)
    hero.use(Armor(name="wall", display="[", bonus=Stats(defence=999)))
    attack(Enemy(hp=15, damage=5), hero)
    assert hero.hp == 99  # max(1, ...) keeps armour from making you immortal
