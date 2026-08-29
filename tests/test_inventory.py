from itergue.combat import Stats
from itergue.entities import ITEM_TYPES
from itergue.inventory import Equipment, Inventory
from itergue.items import Armor, EquipSlot, Weapon

POTION = ITEM_TYPES["SMALL_HEALTH_POTION"]
# ITEM_TYPES is dict[str, Item], and Equipment.equip only accepts Equippable,
# so the equipment tests build their weapon rather than narrowing the table.
SWORD = Weapon(name="Dull Sword", display="/", bonus=Stats(damage=5))


def test_add_returns_true_while_there_is_room():
    bag = Inventory(capacity=2)
    assert bag.add(POTION) is True
    assert bag.add(SWORD) is True
    assert len(bag) == 2


def test_add_refuses_once_the_bag_is_full():
    # The capacity rule finally has an owner. Before Inventory it was written
    # nowhere, so nothing could enforce it.
    bag = Inventory(capacity=1, items=[POTION])
    assert bag.is_full
    assert bag.add(SWORD) is False
    assert list(bag) == [POTION]  # the refused item changed nothing


def test_take_removes_by_index_not_by_equality():
    # Regression: list.remove(bag[2]) deletes the first *equal* item, and
    # ITEM_TYPES hands out shared instances, so asking for index 2 deleted 0.
    bag = Inventory(capacity=5, items=[POTION, SWORD, POTION])
    assert bag.take(2) is POTION
    assert list(bag) == [POTION, SWORD]


def test_getitem_reads_a_slot_without_removing_it():
    bag = Inventory(capacity=5, items=[POTION, SWORD])
    assert bag[1] is SWORD
    assert len(bag) == 2


def test_membership_works_without_a_contains_method():
    bag = Inventory(capacity=5, items=[SWORD])
    assert SWORD in bag
    assert POTION not in bag
    assert hasattr(Inventory, "__contains__") is False  # `in` fell back to __iter__


def test_an_empty_bag_is_falsey_without_a_bool_method():
    assert not Inventory(capacity=5)
    assert Inventory(capacity=5, items=[POTION])
    assert hasattr(Inventory, "__bool__") is False  # bool() fell back to __len__


def test_an_empty_slot_reads_as_none():
    assert Equipment()[EquipSlot.WEAPON] is None


def test_iterating_equipment_terminates():
    # Regression: with only __getitem__, `in` and iteration fell back to the
    # legacy protocol, which called worn.get(0) forever and hung the suite.
    assert list(Equipment()) == []


def test_equip_returns_nothing_when_the_slot_was_empty():
    assert Equipment().equip(SWORD) is None


def test_equip_returns_the_item_it_displaced():
    # Equipment decides that one item fits a slot. Where the old one goes is
    # the game's decision, so equip hands it back instead of filing it away.
    worn = Equipment()
    worn.equip(SWORD)
    dagger = Weapon(name="dagger", display="/", bonus=Stats(damage=3))
    assert worn.equip(dagger) is SWORD
    assert worn[EquipSlot.WEAPON] is dagger


def test_each_item_goes_to_its_own_slot():
    plate = Armor(name="plate", display="[", bonus=Stats(defence=7))
    worn = Equipment()
    assert worn.equip(SWORD) is None
    assert worn.equip(plate) is None  # armour displaces nothing, different slot
    assert (worn[EquipSlot.WEAPON], worn[EquipSlot.ARMOR]) == (SWORD, plate)


def test_bonus_of_nothing_is_the_zero_stats():
    assert Equipment().bonus == Stats()


def test_bonus_sums_every_worn_item():
    worn = Equipment()
    worn.equip(SWORD)  # damage 5
    worn.equip(Armor(name="plate", display="[", bonus=Stats(defence=7)))
    assert worn.bonus == Stats(damage=5, defence=7)
