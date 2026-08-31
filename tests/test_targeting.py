"""Lesson 22: who an effect lands on, and whether it cost you a turn."""

import dataclasses

from itergue.combat import Combatant, attack, nearest, strike
from itergue.enemy import Enemy
from itergue.entities import ITEM_TYPES
from itergue.geometry import Point
from itergue.items import AttackSpell, Consumable, Targeting
from itergue.main import update_state
from itergue.player import Player


def test_nearest_has_nobody_to_return_in_an_empty_room():
    assert nearest(Point(0, 0), []) is None


def test_nearest_measures_in_steps_not_in_a_straight_line():
    # Movement is four-directional, so the only distance this game has is the
    # number of tiles you would walk. A diagonal neighbour is two steps away.
    close = Enemy(name="slime", position=Point(1, 1))  # 2 steps
    far = Enemy(name="orc", position=Point(0, 3))  # 3 steps

    assert nearest(Point(0, 0), [far, close]) is close


def test_aim_sends_a_self_effect_back_to_the_caster():
    hero = Player(position=Point(4, 4))
    orc = Enemy(name="orc", position=Point(5, 4))

    assert hero.aim(Targeting.SELF, [orc]) is hero
    assert hero.aim(Targeting.NEAREST_ENEMY, [orc]) is orc


def test_strike_reports_what_landed_rather_than_what_was_swung():
    orc = Enemy(name="orc", hp=30, defence=4)
    assert strike(10, orc) == 6
    assert orc.hp == 24


def test_armour_never_makes_a_target_immortal():
    wall = Enemy(name="wall", hp=30, defence=999)
    assert strike(10, wall) == 1


def test_attack_and_a_spell_share_one_armour_rule():
    # attack is strike with the initiator's damage. If the two ever disagree,
    # the rule has been written down twice and one copy is already stale.
    hero = Player(hp=50)
    by_hand = Enemy(name="a", hp=30, defence=3)
    by_spell = Enemy(name="b", hp=30, defence=3)

    assert attack(hero, by_hand) == strike(hero.damage, by_spell)
    assert by_hand.hp == by_spell.hp


def test_a_spell_hits_the_nearest_enemy_and_not_the_caster():
    # The bug this lesson closed: consume took a target it was never given.
    hero = Player(position=Point(1, 1), hp=60)
    close = Enemy(name="slime", position=Point(3, 1), hp=20)
    far = Enemy(name="orc", position=Point(9, 1), hp=20)
    hero.inventory.add(ITEM_TYPES["FIRE_BALL"])

    outcome = hero.use(0, 0, [far, close])

    assert close.hp == 15  # 20 - 5 fire ball damage
    assert far.hp == 20
    assert hero.hp == 60
    assert "slime" in outcome.message.text


def test_a_cast_into_an_empty_room_refuses_and_costs_nothing():
    hero = Player(hp=60)
    hero.inventory.add(ITEM_TYPES["FIRE_BALL"])

    outcome = hero.use(0, 0, [])

    assert outcome.spent_turn is False
    assert hero.inventory[0] is ITEM_TYPES["FIRE_BALL"]  # not spent, not cooling


def test_a_spell_on_cooldown_refuses_and_costs_nothing():
    hero = Player(position=Point(1, 1), hp=60)
    orc = Enemy(name="orc", position=Point(4, 1), hp=50)
    hero.inventory.add(ITEM_TYPES["FIRE_BALL"])

    assert hero.use(0, 0, [orc]).spent_turn is True
    refusal = hero.use(0, 1, [orc])

    assert refusal.spent_turn is False
    assert "not ready" in refusal.message.text
    assert orc.hp == 45  # the second press did nothing at all


def test_a_healing_spell_reaches_the_caster_with_no_enemies_present():
    hero = Player(hp=50)
    hero.inventory.add(ITEM_TYPES["SPELL_OF_MINOR_HEALING"])

    assert hero.use(0, 0, []).spent_turn is True
    assert hero.hp == 70


def test_a_refused_action_does_not_advance_the_clock(game):
    # Lesson 21 left this: anything that reached the inventory ended the turn,
    # so a spell on cooldown handed the adjacent orc a free swing.
    game.player.inventory.add(ITEM_TYPES["FIRE_BALL"])
    game.enemies = [Enemy(name="orc", position=Point(6, 5), hp=50, damage=7)]

    update_state(game, ord("1"))  # cast
    hp_after_cast = game.player.hp
    update_state(game, ord("1"))  # on cooldown

    assert game.turn == 1  # the refusal did not move it
    assert game.player.hp == hp_after_cast  # so the orc did not swing twice


def test_every_consumable_in_the_table_declares_who_it_lands_on():
    # The silent failure below, pinned for the shipped items: a consumable that
    # forgets `targeting` stops being consumable and nothing says so.
    for name, item in ITEM_TYPES.items():
        if hasattr(item, "consume"):
            assert isinstance(item, Consumable), f"{name} lost its targeting"


def test_widening_a_protocol_silently_unimplements_its_implementers():
    """isinstance against a protocol is a shape check, and a shape can lose members."""

    @dataclasses.dataclass(frozen=True, slots=True)
    class Poultice:
        name: str = "poultice"
        display: str = "+"

        def consume(self, target: Combatant) -> str:
            target.hp += 5
            return f"{target.name} binds a wound for 5 HP."

    # It has a name and a verb, and before Lesson 22 that was the whole contract.
    # Adding one member to Consumable un-implemented it, with no error anywhere.
    assert not isinstance(Poultice(), Consumable)

    player = Player(name="Kyle", hp=50)
    player.inventory.add(Poultice())  # ty: ignore[invalid-argument-type]
    outcome = player.use(0, 1, [])

    assert outcome.message.text == "You cannot use poultice on its own."
    assert outcome.spent_turn is False
    assert player.hp == 50  # the verb was never reached


def test_targeting_is_a_definition_and_never_a_carried_value():
    # An unannotated class attribute, like slot. dataclasses.replace rebuilds the
    # spell every cast, and a field would have to survive that trip.
    spell = ITEM_TYPES["FIRE_BALL"]
    assert isinstance(spell, AttackSpell)
    assert "targeting" not in {f.name for f in dataclasses.fields(spell)}
    assert dataclasses.replace(spell, ready_at=9).targeting is Targeting.NEAREST_ENEMY
