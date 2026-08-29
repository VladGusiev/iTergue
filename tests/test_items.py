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
    from itergue.items import Weapon

    assert [f.name for f in dataclasses.fields(Weapon)] == ["name", "display", "bonus"]


def test_the_type_table_carries_one_of_each_kind():
    from itergue.items import Armor, Potion, Weapon

    kinds = {type(item) for item in ITEM_TYPES.values()}
    assert kinds == {Potion, Weapon, Armor}
