import dataclasses

import pytest

from itergue.combat import Stats
from itergue.entities import ITEM_TYPES


def test_stats_add_field_by_field():
    assert Stats(damage=10) + Stats(damage=15, defence=2) == Stats(damage=25, defence=2)


def test_adding_stats_leaves_both_operands_alone():
    base = Stats(damage=10)
    bonus = Stats(damage=15)
    base + bonus
    assert (base, bonus) == (Stats(damage=10), Stats(damage=15))


def test_missing_stats_default_to_zero():
    assert Stats(damage=5) == Stats(damage=5, defence=0)


def test_items_are_frozen():
    potion = ITEM_TYPES["SMALL_HEALTH_POTION"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        # ty: ignore[invalid-assignment] - the assignment failing is the point
        potion.heal = 999


def test_the_type_table_hands_out_the_same_instance_every_time():
    # Frozen items are safe to share, so ITEM_TYPES holds objects, not recipes.
    assert ITEM_TYPES["DULL_SWORD"] is ITEM_TYPES["DULL_SWORD"]


def test_no_item_is_drawn_as_a_floor_tile():
    # Regression: a potion with display "." is invisible on the floor.
    from itergue.tiles import RoomObject

    glyphs = {item.display for item in ITEM_TYPES.values()}
    assert RoomObject.FLOOR.value not in glyphs
    assert RoomObject.WALL.value not in glyphs


def test_every_equippable_declares_the_slot_it_belongs_in():
    from itergue.items import Armor, EquipSlot, Weapon

    assert Weapon.slot is EquipSlot.WEAPON
    assert Armor.slot is EquipSlot.ARMOR


def test_slot_is_fixed_per_class_and_not_a_constructor_argument():
    # `slot = EquipSlot.WEAPON` has no annotation, so it is a class attribute,
    # not a field. Every weapon agrees on it and nobody can pass a different one.
    from itergue.items import EquipSlot, Weapon

    assert "slot" not in [f.name for f in dataclasses.fields(Weapon)]
    with pytest.raises(TypeError):
        # ty refuses this statically too, as unknown-argument. The suppression is
        # here to prove the runtime rejects it as well, gate or no gate.
        Weapon(
            name="x",
            display="/",
            bonus=Stats(),
            slot=EquipSlot.ARMOR,  # ty: ignore[unknown-argument]
        )


def test_the_type_table_carries_one_of_each_kind():
    from typing import get_args

    from itergue.items import Item

    kinds = {type(item) for item in ITEM_TYPES.values()}
    # Reading the union means a new item kind fails here until the table has one,
    # instead of this list going stale every time Item grows.
    assert kinds == set(get_args(Item))


def test_a_potion_and_a_spell_are_consumable_without_inheriting_anything():
    from itergue.items import Consumable, Potion, Spell

    assert isinstance(ITEM_TYPES["SMALL_HEALTH_POTION"], Consumable)
    assert isinstance(ITEM_TYPES["RESTING_SPELL"], Consumable)
    # Structural, not nominal: neither class has Consumable anywhere above it.
    assert Consumable not in Potion.__mro__
    assert Consumable not in Spell.__mro__


def test_the_equippable_union_is_exactly_the_two_slot_types():
    from typing import get_args

    from itergue.items import Armor, Equippable, EquipSlot, Weapon

    # The closed axis, pinned. A third slot has to grow both of these together.
    assert get_args(Equippable) == (Weapon, Armor)
    assert len(EquipSlot) == 2


def test_the_table_is_a_definition_and_a_cast_never_touches_it():
    from itergue.items import Spell
    from itergue.player import Player

    definition = ITEM_TYPES["RESTING_SPELL"]
    hero = Player(hp=50)
    hero.inventory.add(definition)
    hero.use(0, turn=0)
    carried = hero.inventory[0]

    # ITEM_TYPES is dict[str, Item], so reading a Spell field needs the narrowing
    # assert. In a test that is documentation, not ceremony.
    assert isinstance(definition, Spell) and isinstance(carried, Spell)
    assert definition.ready_at == 0  # the table is a definition, not a carrier
    assert carried.ready_at == 3
    assert carried is not definition


def test_two_carriers_of_one_definition_have_their_own_clocks():
    from itergue.player import Player

    hero, rival = Player(name="Kyle", hp=50), Player(name="Rival", hp=50)
    for carrier in (hero, rival):
        carrier.inventory.add(ITEM_TYPES["RESTING_SPELL"])

    hero.use(0, turn=0)
    assert "cooldown" in hero.use(0, turn=1).text
    assert "healed" in rival.use(0, turn=1).text  # one definition, separate clocks


def test_the_cooldown_blocks_then_expires():
    from itergue.player import Player

    hero = Player(hp=50)
    hero.inventory.add(ITEM_TYPES["RESTING_SPELL"])

    assert "healed" in hero.use(0, turn=0).text
    assert "cooldown" in hero.use(0, turn=2).text
    assert "healed" in hero.use(0, turn=3).text  # ready_at == 0 + cooldown


def test_a_potion_is_spent_and_a_spell_is_only_unavailable():
    from itergue.player import Player

    hero = Player(hp=50)
    hero.inventory.add(ITEM_TYPES["SMALL_HEALTH_POTION"])
    hero.inventory.add(ITEM_TYPES["RESTING_SPELL"])

    hero.use(0, turn=0)  # the potion is gone, so the spell shifts into slot 0
    assert len(hero.inventory) == 1

    hero.use(0, turn=0)  # a cast leaves the spell where it is
    assert len(hero.inventory) == 1


def test_every_item_the_player_can_pick_up_describes_itself():
    # The default is "", so the only thing stopping a new item shipping without
    # a description is this test.
    assert all(item.description for item in ITEM_TYPES.values())


def test_no_description_gives_the_numbers_away():
    # The player is meant to find the numbers by playing, not by reading.
    assert not any(
        character.isdigit()
        for item in ITEM_TYPES.values()
        for character in item.description
    )


def test_the_bag_screen_fits_a_narrow_terminal():
    from itergue.player import Player
    from itergue.render import bag_lines

    player = Player()
    for item in list(ITEM_TYPES.values()) * 2:
        player.inventory.add(item)

    assert player.inventory.is_full
    assert max(len(line) for line in bag_lines(player)) < 80
