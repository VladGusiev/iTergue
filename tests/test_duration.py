"""Lesson 23: effects that outlive the turn that started them.

Two clocks meet here. An Effect carries a deadline, and Game.turn is the only
thing that can tell it the deadline has passed.
"""

import inspect
from typing import cast

from itergue.combat import Combatant, Effect, Stats
from itergue.enemy import Enemy
from itergue.entities import ITEM_TYPES
from itergue.game import Game
from itergue.geometry import Point
from itergue.items import BuffPotion, Consumable, Freezing, Lasting, TimeSpell
from itergue.main import update_state
from itergue.player import Player

# The table is typed as the whole Item union, so narrow once here rather than
# reaching for `.duration` or `.freeze` through a union that mostly lacks them.
RAGE = cast(BuffPotion, ITEM_TYPES["RAGE_POTION"])
TIME_STOP = cast(TimeSpell, ITEM_TYPES["TIME_STOP"])
SLOT_1 = ord("1")


# --- the query that must not learn the time -------------------------------


def test_stats_with_no_effects_returns_the_worn_total_untouched():
    # sum over an empty generator returns the start value. Not a special case,
    # just the reason `stats` needs no branch for the common state of the game.
    hero = Player()
    assert hero.effects == []
    assert hero.stats == Stats(damage=10)


def test_stats_adds_every_live_effect_on_top_of_what_is_worn():
    hero = Player()
    hero.effects = [
        Effect("Rage Potion", Stats(damage=8), expires_at=5),
        Effect("Stoneskin", Stats(defence=2), expires_at=9),
    ]
    assert hero.stats == Stats(damage=18, defence=2)


def test_stats_takes_no_turn_argument():
    # If it did, `damage` would become a bound method rather than an int and the
    # Player would stop satisfying Combatant. The protocol is what forbids this.
    assert list(inspect.signature(Player.stats.fget).parameters) == ["self"]
    assert isinstance(Player(), Combatant)


def test_expire_effects_returns_what_ended_and_keeps_what_did_not():
    hero = Player()
    gone = Effect("Rage Potion", Stats(damage=8), expires_at=3)
    stays = Effect("Stoneskin", Stats(defence=2), expires_at=9)
    hero.effects = [gone, stays]

    assert hero.expire_effects(4) == [gone]
    assert hero.effects == [stays]


def test_an_effect_lives_through_the_turn_it_expires_on():
    # expires_at is a deadline, not a countdown, so the boundary is `turn >`.
    hero = Player()
    hero.effects = [Effect("Rage Potion", Stats(damage=8), expires_at=5)]

    assert hero.expire_effects(5) == []
    assert hero.stats.damage == 18


# --- the widening that was affordable -------------------------------------


def test_both_fighters_carry_effects():
    # Combatant gained a member in Lesson 23 and both implementers kept up. In
    # Lesson 22 one did not, and every gate stayed green. This is that check.
    assert isinstance(Player(), Combatant)
    assert isinstance(Enemy(), Combatant)


def test_each_fighter_gets_its_own_effects_list():
    assert Player().effects is not Player().effects
    assert Enemy().effects is not Enemy().effects


def test_every_consumable_in_the_table_still_declares_who_it_lands_on():
    for key, item in ITEM_TYPES.items():
        if hasattr(item, "consume"):
            assert isinstance(item, Consumable), f"{key} stopped being usable"


def test_the_table_really_holds_the_types_this_file_casts_it_to():
    # The two constants at the top are cast, so something has to check they are
    # honest. If the table changes shape, this is what says so.
    assert isinstance(ITEM_TYPES["RAGE_POTION"], BuffPotion)
    assert isinstance(ITEM_TYPES["TIME_STOP"], TimeSpell)


def test_only_the_items_that_should_be_lasting_or_freezing_are():
    lasting = {k for k, v in ITEM_TYPES.items() if isinstance(v, Lasting)}
    freezing = {k for k, v in ITEM_TYPES.items() if isinstance(v, Freezing)}
    # Weapon and Armor have a `bonus` too. `duration` is what keeps them out.
    assert lasting == {"RAGE_POTION"}
    assert freezing == {"TIME_STOP"}


# --- applying a lasting effect --------------------------------------------


def test_drinking_a_buff_potion_leaves_an_effect_with_a_deadline(use):
    hero = Player()
    use(hero, RAGE, turn=4)

    assert [e.expires_at for e in hero.effects] == [4 + RAGE.duration]
    assert hero.damage == 18


def test_a_buff_potion_is_still_consumed_on_the_turn_it_is_drunk(use):
    hero = Player()
    use(hero, RAGE)
    assert len(hero.inventory) == 0


def test_a_one_shot_consumable_leaves_nothing_behind(use):
    hero = Player(hp=50)
    use(hero, ITEM_TYPES["SMALL_HEALTH_POTION"])
    assert hero.effects == []


def test_apply_puts_the_effect_on_the_target_not_on_the_caster():
    # Nothing is aimed at an enemy yet, but apply is what decides, so pin it.
    hero = Player()
    orc = Enemy(name="orc")
    hero.apply(RAGE, orc, turn=0)

    assert hero.effects == []
    assert [e.name for e in orc.effects] == ["Rage Potion"]


# --- the guard that has to stay above the command -------------------------


def test_a_refused_cast_does_not_apply_its_effect(use):
    # The bug this pins: `apply` is a command, so hoisting it above the cooldown
    # guard spends the effect on an action that then refuses. Cast, then spam.
    hero = Player()
    use(hero, TIME_STOP, turn=0)
    for turn in range(1, TIME_STOP.cooldown):
        outcome = hero.use(0, turn, [])
        assert outcome.spent_turn is False
        assert outcome.freeze_turns == 0

    assert hero.effects == []


# --- the clock ------------------------------------------------------------


def test_a_buff_lasts_exactly_as_many_turns_as_its_duration(level, use):
    hero = Player(position=Point(5, 5))
    game = Game(level=level, player=hero, enemies=[])
    use(hero, RAGE, turn=game.turn)

    buffed = 0
    for _ in range(RAGE.duration + 3):
        game.end_turn()
        if hero.damage > 10:
            buffed += 1

    # Pruning after the increment. Move it above and this becomes duration + 1,
    # with nothing in the toolchain to tell you the field name started lying.
    assert buffed == RAGE.duration


def test_the_player_is_told_when_an_effect_wears_off(level):
    hero = Player(position=Point(5, 5))
    hero.effects = [Effect("Rage Potion", Stats(damage=8), expires_at=0)]
    game = Game(level=level, player=hero, enemies=[])
    game.end_turn()

    assert any("Rage Potion wears off." == m.text for m in game.messages)


# --- the effect that is not on anybody ------------------------------------


def test_time_stop_leaves_through_the_outcome_rather_than_the_target(use):
    # consume is only ever handed a Combatant, so an effect on the world has to
    # travel back out through the channel Lesson 22 built.
    hero = Player()
    outcome = use(hero, TIME_STOP)

    assert outcome.freeze_turns == TIME_STOP.freeze
    assert hero.effects == []


def test_an_ordinary_consumable_freezes_nothing(use):
    assert use(Player(hp=50), ITEM_TYPES["SMALL_HEALTH_POTION"]).freeze_turns == 0


def test_time_stop_buys_exactly_its_freeze_in_free_turns(level):
    hero = Player(position=Point(5, 5))
    orc = Enemy(name="orc", position=Point(6, 5), hp=100, damage=10)
    game = Game(level=level, player=hero, enemies=[orc])
    hero.inventory.add(TIME_STOP)

    update_state(game, SLOT_1)  # casting ends a turn, so this is the first free one
    hp_by_turn = [hero.hp]
    for _ in range(3):
        game.end_turn()
        hp_by_turn.append(hero.hp)

    # Turns 1, 2 and 3 cost nothing. On turn 4 the orc is next to you again.
    assert hp_by_turn == [100, 100, 100, 90]


def test_the_cast_turn_is_itself_the_first_frozen_turn(level):
    # end_turn increments before it reads frozen_until, which is where the +1 in
    # player_acts comes from. Off by one here and you get a spell that lies.
    game = Game(level=level, player=Player(position=Point(5, 5)), enemies=[])
    game.player.inventory.add(TIME_STOP)

    update_state(game, SLOT_1)
    assert (game.turn, game.frozen_until) == (1, TIME_STOP.freeze + 1)


def test_a_game_that_never_froze_has_no_frozen_turns(level):
    game = Game(level=level, player=Player(), enemies=[])
    assert game.frozen_until == 0
    game.end_turn()
    assert game.turn == 1  # 1 < 0 is false, so nothing is skipped


def test_the_time_spell_cools_down_like_any_other_spell(use):
    hero = Player()
    use(hero, TIME_STOP, turn=0)
    cooling = hero.inventory[0]
    assert isinstance(cooling, TimeSpell)  # a new value in the slot, same type
    assert cooling.ready_at == TIME_STOP.cooldown
