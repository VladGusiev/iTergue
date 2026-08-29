from itergue.enemy import Enemy
from itergue.entities import ITEM_TYPES
from itergue.geometry import Point
from itergue.main import update_state
from itergue.player import Player


def test_bump_attack_kills_enemy_and_player_holds(game):
    game.enemies = [Enemy(position=Point(6, 5), hp=10)]  # right of player at (5, 5)
    update_state(game, ord("l"))
    assert game.enemies == []  # killed: player dmg 10 == enemy hp 10
    assert game.player.position == Point(5, 5)  # attacked, did not move


def test_move_into_empty_floor(game):
    update_state(game, ord("l"))
    assert game.player.position == Point(6, 5)


def test_wall_blocks_movement(game):
    game.player = Player(position=Point(1, 1))  # column x=0 is a wall
    update_state(game, ord("h"))
    assert game.player.position == Point(1, 1)


def test_unknown_key_leaves_the_player_where_they_are(game):
    update_state(game, ord("x"))
    assert game.player.position == Point(5, 5)


def test_second_enemy_attacks_after_first_enemy_dies(game):
    game.enemies = [
        Enemy(position=Point(6, 5), hp=10, damage=3),
        Enemy(position=Point(7, 5), hp=10, damage=3),
    ]
    update_state(game, ord("l"))
    assert len(game.enemies) == 1  # first enemy killed
    assert game.player.hp == 100


def test_surviving_enemy_retaliates_once(game):
    game.enemies = [Enemy(position=Point(6, 5), hp=20, damage=3)]
    update_state(game, ord("l"))
    assert game.enemies[0].hp == 10
    assert game.player.hp == 97


def test_walking_onto_an_item_picks_it_up(game):
    potion = ITEM_TYPES["SMALL_HEALTH_POTION"]
    game.floor_items = {Point(6, 5): potion}  # right of the player

    update_state(game, ord("l"))

    assert game.player.inventory == [potion]
    assert game.floor_items == {}  # taken from the floor, not copied
    assert "pick up" in game.messages[-1].text


def test_walking_onto_an_item_does_not_use_it(game):
    game.floor_items = {Point(6, 5): ITEM_TYPES["SMALL_HEALTH_POTION"]}
    game.player.hp = 50

    update_state(game, ord("l"))

    assert game.player.hp == 50  # picking up is not drinking


def test_walking_past_an_item_leaves_it_alone(game):
    game.floor_items = {Point(9, 9): ITEM_TYPES["SMALL_HEALTH_POTION"]}
    update_state(game, ord("l"))
    assert game.player.inventory == []
    assert len(game.floor_items) == 1


def test_a_slot_key_uses_that_item(game):
    game.player.hp = 50
    game.player.inventory = [ITEM_TYPES["SMALL_HEALTH_POTION"]]

    update_state(game, ord("1"))

    assert game.player.hp == 70
    assert game.player.inventory == []  # consumed
    assert game.player.position == Point(5, 5)  # using an item is not a move


def test_a_slot_key_for_an_empty_slot_does_nothing(game):
    update_state(game, ord("1"))
    assert game.player.inventory == []
    assert list(game.messages) == []


def test_enemies_still_take_their_turn_when_you_use_an_item(game):
    # Regression: an early return here used to hand every enemy a free pass.
    game.player.inventory = [ITEM_TYPES["SMALL_HEALTH_POTION"]]
    game.enemies = [Enemy(name="orc", position=Point(6, 5), damage=3)]

    update_state(game, ord("1"))

    assert game.player.hp == 100 + 20 - 3  # healed, then hit by the adjacent orc


def test_equipping_from_the_bag_raises_the_damage_you_attack_with(game):
    game.player.inventory = [ITEM_TYPES["DULL_SWORD"]]
    game.enemies = [Enemy(name="orc", position=Point(6, 5), hp=50, damage=0)]

    update_state(game, ord("1"))  # wield
    update_state(game, ord("l"))  # attack

    assert game.enemies[0].hp == 35  # 50 - (10 base + 5 sword)
