from itergue.controls import CONTROLS, HELP, MOVE, QUIT, SLOT, SWAP, Control
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
    # render_hud numbers the bag from 1, so 1-9 is what the labels promise.
    assert SLOT.keys == {ord(digit) for digit in "123456789"}


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
