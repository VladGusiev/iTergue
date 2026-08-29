import pytest

from itergue.combat import Stats
from itergue.entities import ITEM_TYPES
from itergue.geometry import Point
from itergue.items import Armor, EquipSlot, Potion, Weapon
from itergue.player import Player


@pytest.mark.parametrize(
    "keycode, expected",
    [
        (ord("k"), Point(5, 4)),  # UP
        (ord("l"), Point(6, 5)),  # RIGHT
        (ord("j"), Point(5, 6)),  # DOWN
        (ord("h"), Point(4, 5)),  # LEFT
        (ord("x"), Point(5, 5)),  # unknown key → no move
    ],
)
def test_proposed_position_return_point(player, keycode, expected):
    result = player.proposed_position(keycode)
    assert isinstance(result, Point)
    assert result == expected


def test_proposed_position_does_not_move_the_player(player):
    player.proposed_position(ord("l"))
    assert player.position == Point(5, 5)  # it proposes, it does not commit


def test_players_does_not_share_inventory():
    player1 = Player()
    player2 = Player()
    sword = ITEM_TYPES["DULL_SWORD"]
    player1.inventory.add(sword)
    assert list(player1.inventory) == [sword]
    assert list(player2.inventory) == []


def test_every_slot_starts_empty(player):
    assert list(player.equipment) == []
    assert all(player.equipment[slot] is None for slot in EquipSlot)
    assert [slot.value for slot in EquipSlot] == ["Weapon", "Armor"]


def test_damage_is_the_base_until_something_is_equipped(player):
    assert player.damage == player.base.damage == 10


def test_using_a_potion_heals_the_player():
    player = Player(hp=50)
    message = player.use(Potion(name="tonic", display="!", heal=20))
    assert player.hp == 70
    assert "tonic" in message


def test_equipping_a_weapon_raises_damage_without_storing_it(player):
    axe = Weapon(name="axe", display="/", bonus=Stats(damage=15))

    message = player.use(axe)

    assert player.equipment[EquipSlot.WEAPON] is axe
    assert player.equipment[EquipSlot.ARMOR] is None  # the other slot is untouched
    assert player.damage == 25  # derived: 10 base + 15 bonus
    assert player.base == Stats(damage=10)  # the base was never written to
    assert "axe" in message


def test_unequipping_restores_the_base_damage(player):
    player.use(Weapon(name="axe", display="/", bonus=Stats(damage=15)))
    # ponytail: no unequip verb yet, so reach into worn. Add Equipment.unequip
    # when something in the game actually takes a weapon off.
    player.equipment.worn.clear()
    assert player.damage == 10  # nothing to undo, because nothing was overwritten


def test_equipping_a_second_weapon_replaces_the_first(player):
    axe = Weapon(name="axe", display="/", bonus=Stats(damage=15))
    dagger = Weapon(name="dagger", display="/", bonus=Stats(damage=3))
    player.use(axe)
    player.use(dagger)
    assert player.damage == 13  # one slot, so bonuses replace and do not stack


def test_the_weapon_you_replace_goes_back_into_the_bag(player):
    axe = Weapon(name="axe", display="/", bonus=Stats(damage=15))
    player.use(axe)
    player.use(Weapon(name="dagger", display="/", bonus=Stats(damage=3)))
    assert list(player.inventory) == [axe]  # swapped out, not destroyed


def test_stats_sum_over_every_filled_slot(player):
    player.use(Weapon(name="axe", display="/", bonus=Stats(damage=15)))
    player.use(Armor(name="plate", display="[", bonus=Stats(defence=7)))
    assert player.stats == Stats(damage=25, defence=7)
    assert player.damage == 25 and player.defence == 7  # both read the same sum


def test_a_potion_does_not_touch_damage_and_a_weapon_does_not_touch_hp(player):
    player.hp = 50
    player.use(Potion(name="tonic", display="!", heal=20))
    assert player.damage == 10
    player.use(Weapon(name="axe", display="/", bonus=Stats(damage=15)))
    assert player.hp == 70
