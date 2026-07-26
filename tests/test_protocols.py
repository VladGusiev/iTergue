from itergue.combat import Combatant, attack
from itergue.enemy import Enemy
from itergue.player import Player


def test_player_and_enemy_are_combatants():
    player = Player(x=0, y=0)
    enemy = Enemy(x=1, y=1)
    assert isinstance(player, Combatant)
    assert isinstance(enemy, Combatant)


def test_attack_does_not_reduces_hp():
    hero = Player(x=0, y=0, hp=20, damage=5)
    monster = Enemy(x=1, y=1, hp=15, damage=3)
    attack(hero, monster)
    assert monster.hp == 10  # 15 - 5
    assert hero.hp == 20
