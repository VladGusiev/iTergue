from itergue.controls import (
    CONTROLS,
    HELP,
    MOVE,
    QUIT,
    SLOT,
    SLOT_INDEX,
    SLOTS,
    SWAP,
    Control,
)
from itergue.tiles import Direction


def test_no_two_controls_claim_the_same_key():
    # The one failure a help screen cannot show you: it lists a key that does
    # something else. Pressing it would take the first matching branch silently.
    claimed = [key for control in CONTROLS for key in control.keys]
    assert len(claimed) == len(set(claimed))


def test_movement_keys_come_from_direction_and_cannot_drift():
    assert MOVE.keys == {direction.value for direction in Direction}


def test_every_control_is_reachable_from_a_terminal():
    # curses.getch returns an int per keypress, so anything above 255 could
    # never arrive as a plain character.
    assert all(0 <= key < 256 for control in CONTROLS for key in control.keys)


def test_both_cases_of_the_action_keys_are_bound():
    assert SWAP.keys == {ord("s"), ord("S")}
    assert QUIT.keys == {ord("q"), ord("Q")}


def test_slot_keys_cover_the_digits_the_hud_numbers():
    # The HUD labels the bag with SLOTS, so those are the keys that must act.
    assert SLOT.keys == {ord(digit) for digit in SLOTS}


def test_every_slot_the_bag_can_hold_has_a_key_that_reaches_it():
    # Regression: 1-9 against a capacity of 10 left the tenth item unusable.
    # It could be picked up, seen and dropped, but never used.
    from itergue.inventory import Inventory

    assert len(SLOT_INDEX) == Inventory().capacity
    assert SLOT_INDEX[ord("0")] == Inventory().capacity - 1


def test_the_hud_bag_summary_fits_a_narrow_terminal():
    # Regression: names on the HUD line made it 205 characters, and render
    # sliced it to the terminal width without saying anything was missing.
    from itergue.entities import ITEM_TYPES
    from itergue.player import Player
    from itergue.render import carried_line

    player = Player()
    for item in list(ITEM_TYPES.values()) * 2:
        player.inventory.add(item)

    assert player.inventory.is_full
    stats = f"HP: {player.hp}  Damage: {player.damage}  Carried: {carried_line(player)}"
    assert len(stats) < 80


def test_every_control_has_a_label_and_a_description():
    assert all(control.label and control.description for control in CONTROLS)
    assert HELP in CONTROLS  # the screen has to list the key that opens it


def test_a_control_is_immutable():
    assert isinstance(SWAP, tuple)
    assert Control("x", "test", frozenset(b"x")) == ("x", "test", frozenset(b"x"))


def test_the_footer_names_the_help_and_quit_keys():
    from itergue.render import FOOTER

    assert HELP.label in FOOTER
    assert QUIT.label.upper() in FOOTER


def test_an_overlay_block_is_centred_on_the_screen():
    from itergue.render import centered_block

    block, top, left = centered_block("Bag", ["a", "bb"], width=40, height=20)

    assert block[0].strip() == "Bag"
    assert block[-1].strip() == "Press any key to return"
    assert len(block) == 6  # title, blank, two lines, blank, footer
    assert (top, left) == ((20 - len(block)) // 2, (40 - len(block[-1])) // 2)


def test_a_screen_too_small_for_the_block_starts_at_the_corner():
    # Negative coordinates are a curses error, not a layout; clamp instead.
    from itergue.render import centered_block

    _, top, left = centered_block("Controls", ["x" * 100], width=10, height=2)

    assert (top, left) == (0, 0)
