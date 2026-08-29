from collections import deque

from itergue.enemy import Enemy
from itergue.game import MESSAGE_LOG_SIZE, Game, Message, MessageKind
from itergue.geometry import Point
from itergue.main import update_state


def test_log_keeps_only_the_most_recent_messages(game):
    for turn in range(MESSAGE_LOG_SIZE + 3):
        game.log(f"turn {turn}")
    assert len(game.messages) == MESSAGE_LOG_SIZE
    assert game.messages[0].text == "turn 3"  # the first three fell off the front
    assert game.messages[-1].text == f"turn {MESSAGE_LOG_SIZE + 2}"


def test_each_game_gets_its_own_log(level, player):
    first = Game(level=level, player=player, enemies=[])
    second = Game(level=level, player=player, enemies=[])
    first.log("only mine")
    assert first.messages == deque([Message("only mine", MessageKind.INFO)])
    assert second.messages == deque()


def test_remove_dead_enemies_filters_every_corpse(game):
    # Regression: removing while iterating used to skip an enemy after a removed one.
    game.enemies = [
        Enemy(position=Point(1, 1), hp=0),
        Enemy(position=Point(2, 2), hp=0),
        Enemy(position=Point(3, 3), hp=5),
    ]
    game.remove_dead_enemies()
    assert [enemy.hp for enemy in game.enemies] == [5]


def test_hitting_a_survivor_logs_both_sides_of_the_exchange(game):
    game.enemies = [Enemy(name="orc", position=Point(6, 5), hp=20, damage=3)]
    update_state(game, ord("l"))
    assert list(game.messages) == [
        Message("You attack the orc for 10 damage!", MessageKind.GOOD),
        Message("The orc attacks you for 3 damage!", MessageKind.BAD),
    ]


def test_killing_an_enemy_logs_its_death(game):
    game.enemies = [Enemy(name="slime", position=Point(6, 5), hp=10)]
    update_state(game, ord("l"))
    assert list(game.messages) == [
        Message("You attack the slime for 10 damage!", MessageKind.GOOD),
        Message("The slime dies!", MessageKind.GOOD),
    ]


def test_a_quiet_turn_logs_nothing(game):
    update_state(game, ord("l"))
    assert list(game.messages) == []
