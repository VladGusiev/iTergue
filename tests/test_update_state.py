from itergue.enemy import Enemy
from itergue.entities import ITEM_TYPES
from itergue.geometry import Point
from itergue.inventory import Inventory
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

    assert list(game.player.inventory) == [potion]
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
    assert list(game.player.inventory) == []
    assert len(game.floor_items) == 1


def test_a_slot_key_uses_that_item(game):
    game.player.hp = 50
    game.player.inventory.add(ITEM_TYPES["SMALL_HEALTH_POTION"])

    update_state(game, ord("1"))

    assert game.player.hp == 70
    assert list(game.player.inventory) == []  # consumed
    assert game.player.position == Point(5, 5)  # using an item is not a move


def test_a_slot_key_for_an_empty_slot_does_nothing(game):
    update_state(game, ord("1"))
    assert list(game.player.inventory) == []
    assert list(game.messages) == []


def test_enemies_still_take_their_turn_when_you_use_an_item(game):
    # Regression: an early return here used to hand every enemy a free pass.
    game.player.inventory.add(ITEM_TYPES["SMALL_HEALTH_POTION"])
    game.enemies = [Enemy(name="orc", position=Point(6, 5), damage=3)]

    update_state(game, ord("1"))

    assert game.player.hp == 100 + 20 - 3  # healed, then hit by the adjacent orc


def test_equipping_from_the_bag_raises_the_damage_you_attack_with(game):
    game.player.inventory.add(ITEM_TYPES["DULL_SWORD"])
    game.enemies = [Enemy(name="orc", position=Point(6, 5), hp=50, damage=0)]

    update_state(game, ord("1"))  # wield
    update_state(game, ord("l"))  # attack

    assert game.enemies[0].hp == 35  # 50 - (10 base + 5 sword)


def test_a_full_pack_leaves_the_item_on_the_floor(game):
    # Walking is free. A full pack refuses the item and costs you nothing,
    # so you never lose a slot by crossing a tile you did not care about.
    sword = ITEM_TYPES["DULL_SWORD"]
    game.player.inventory = Inventory(
        capacity=1, items=[ITEM_TYPES["SMALL_HEALTH_POTION"]]
    )
    game.floor_items = {Point(6, 5): sword}

    update_state(game, ord("l"))

    assert "no room" in game.messages[-1].text
    assert game.floor_items == {Point(6, 5): sword}  # still there to come back for
    assert sword not in game.player.inventory


def test_s_swaps_the_last_slot_for_what_you_are_standing_on(game):
    potion, sword = ITEM_TYPES["SMALL_HEALTH_POTION"], ITEM_TYPES["DULL_SWORD"]
    armor = ITEM_TYPES["RUSTY_ARMOR"]
    game.player.inventory = Inventory(capacity=2, items=[potion, sword])
    game.floor_items = {Point(6, 5): armor}

    update_state(game, ord("l"))  # step on it, pack is full, it stays put
    update_state(game, ord("s"))  # now ask for the trade

    assert list(game.player.inventory) == [potion, armor]  # last slot, not the first
    assert game.floor_items == {Point(6, 5): sword}  # traded, not destroyed
    assert "swap" in game.messages[-1].text


def test_s_on_a_bare_tile_says_so(game):
    update_state(game, ord("s"))
    assert "nothing here" in game.messages[-1].text
    assert list(game.player.inventory) == []


def test_s_just_picks_up_when_there_is_room(game):
    # Reachable after drinking a potion frees a slot while you stand on an item.
    armor = ITEM_TYPES["RUSTY_ARMOR"]
    game.floor_items = {Point(5, 5): armor}  # under the player

    update_state(game, ord("s"))

    assert list(game.player.inventory) == [armor]
    assert game.floor_items == {}
    assert "pick up" in game.messages[-1].text


def test_s_does_not_move_you_or_skip_the_enemy_turn(game):
    game.player.inventory = Inventory(capacity=1, items=[ITEM_TYPES["DULL_SWORD"]])
    game.floor_items = {Point(5, 5): ITEM_TYPES["RUSTY_ARMOR"]}
    game.enemies = [Enemy(name="orc", position=Point(6, 5), damage=4)]

    update_state(game, ord("s"))

    assert game.player.position == Point(5, 5)  # swapping is not a move
    assert game.player.hp == 96  # the orc still got its turn


def test_armor_from_the_bag_soaks_damage(game):
    game.player.inventory.add(ITEM_TYPES["RUSTY_ARMOR"])  # defence 3
    game.enemies = [Enemy(name="orc", position=Point(6, 5), hp=50, damage=10)]

    update_state(game, ord("1"))  # wear it, and the orc gets its turn

    assert game.player.hp == 93  # 100 - max(1, 10 - 3)


def test_an_unbound_key_costs_the_player_nothing(game):
    # Regression: every key that meant nothing still ended the turn, so pressing
    # an arrow key handed every enemy on the level a free move and a free hit.
    game.enemies = [Enemy(position=Point(6, 5), hp=10, damage=3)]

    update_state(game, ord("x"))

    assert game.turn == 0
    assert game.player.hp == 100
    assert game.enemies[0].position == Point(6, 5)


def test_an_unbound_key_does_not_pick_up_what_you_are_standing_on(game):
    # Regression: an unbound key fell through to the move branch, "moved" the
    # player onto the tile they were already on, and picked the tile up.
    game.floor_items[game.player.position] = ITEM_TYPES["CHEST_KEY"]

    update_state(game, ord("x"))

    assert len(game.player.inventory) == 0
    assert game.player.position in game.floor_items


def test_walking_into_a_wall_costs_no_turn(game):
    game.player = Player(position=Point(1, 1))  # column x=0 is a wall

    update_state(game, ord("h"))

    assert game.turn == 0


def test_a_move_that_happens_costs_exactly_one_turn(game):
    update_state(game, ord("l"))

    assert game.turn == 1


def test_every_screen_has_the_shape_show_screen_promises(game):
    # ScreenDrawer is (window, Game) -> None. Nothing checks that at runtime, so
    # this pins the signature the game loop actually calls them with.
    from inspect import signature

    from itergue.render import render_bag, render_controls

    for screen in (render_bag, render_controls):
        assert [p.name for p in signature(screen).parameters.values()] == [
            "stdscr",
            "game",
        ]
