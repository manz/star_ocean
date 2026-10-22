"""Scene 80's door console, played in the patched game from a real arrival (tests/warp.py): the French password
GAÏA opens the door with either A as the second letter, a wrong one does not (tools/scene_events.py).

The console room is map 164; `var.w[0x10]` 144 is the story point where the console asks for the password, and the
door branch increments it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.screens import assert_matches_golden
from tests.warp import field, press, press_until, set_var, walk, warp

if TYPE_CHECKING:
    from kintsuki import Emu

PROGRESS = 0x10
ASKING, OPENED = 144, 145
SET_4 = "RIGHT,RIGHT,RIGHT,A"  # A I G A
G = "RIGHT,RIGHT,A"  # slot 3 of 1 A, 2 I, 3 G, 4 A
FIRST_A, LAST_A = "A", "RIGHT,RIGHT,A"  # left: 1 A, 2 I, 3 A
I_AFTER_FIRST_A, I_AFTER_LAST_A = "A", "RIGHT,A"  # left: 1 I, 2 A / 1 A, 2 I
A_AFTER_LAST_A = "A"
GAIA_LINE = 0x436  # `say_mode0 14` (GAÏA ?) waiting on its window


def _console() -> Emu:
    """In front of the console, its password prompt about to open."""
    emu = field("fantasyanime_4")
    set_var(emu, PROGRESS, ASKING)
    warp(emu, 164, 8, 8, 2)
    walk(emu, "RIGHT", 16)  # into the box syscall 22 tests: tiles x 11-13, y 8-9
    walk(emu, "UP", 2)  # facing up: the A script first tests the hero's facing (actor +0x18) == 0
    return emu


def _enter(emu: Emu, second: str, third: str) -> None:
    press(emu, f"A,A,{SET_4},A,{G},A,{second},A,{third}")


@pytest.mark.parametrize(("second", "third"), [(FIRST_A, I_AFTER_FIRST_A), (LAST_A, I_AFTER_LAST_A)])
def test_gaia_opens_the_door(second: str, third: str) -> None:
    emu = _console()
    _enter(emu, second, third)
    assert emu.read16(0x7EFEC3 + PROGRESS) == OPENED


def test_a_wrong_third_letter_keeps_it_shut() -> None:
    emu = _console()
    _enter(emu, LAST_A, A_AFTER_LAST_A)
    letters = bytes(emu.read_range(0x7EFEC3 + 0x4C, 4))  # set, then the slot of letters 1-3
    assert (letters.hex(" "), emu.read16(0x7EFEC3 + PROGRESS)) == ("04 03 04 01", ASKING)


def test_the_reveal_reads_gaia() -> None:
    emu = _console()
    _enter(emu, FIRST_A, I_AFTER_FIRST_A)
    press_until(emu, GAIA_LINE)
    assert_matches_golden(emu, "scene80_gaia")
