from itergue.combat import Combatant, attack
from itergue.enemy import Enemy
from itergue.player import Player


def test_player_and_enemy_are_combatants():
    # Position is irrelevant here: Combatant only asks for hp and damage.
    assert isinstance(Player(), Combatant)
    assert isinstance(Enemy(), Combatant)


def test_attack_does_not_reduces_hp():
    hero = Player(hp=20, damage=5)
    monster = Enemy(hp=15, damage=3)
    attack(hero, monster)
    assert monster.hp == 10  # 15 - 5
    assert hero.hp == 20
