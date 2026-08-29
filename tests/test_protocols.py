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
