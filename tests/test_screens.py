"""The French menus as the game draws them (tests/screens.py)."""

from __future__ import annotations

import pytest

from tests.screens import assert_matches_golden, emulator, tap

MAIN_MENU = "A,A,A,X"  # load screen: slot 1, confirm, then the menu button

SCREENS = {
    "load": ("title_continue", "A,A,A"),
    "main_menu": ("load_screen", MAIN_MENU),
    "items": ("load_screen", f"{MAIN_MENU},RIGHT,A,DOWN,RIGHT"),
    "group": ("load_screen", f"{MAIN_MENU},RIGHT,RIGHT,A"),
    "strategy": ("load_screen", f"{MAIN_MENU},RIGHT,RIGHT,A,A"),
    "formation": ("load_screen", f"{MAIN_MENU},RIGHT,RIGHT,A,DOWN,DOWN,A"),
    "settings": ("load_screen", f"{MAIN_MENU},RIGHT,RIGHT,RIGHT,A"),
    "settings_sound": ("load_screen", f"{MAIN_MENU},RIGHT,RIGHT,RIGHT,A,UP,DOWN,RIGHT"),
    "chest": ("chest", "A"),  # facing a chest: the item found message
}
SETTLE = {"chest": 120}  # frames more for text that types itself out


@pytest.mark.parametrize("name", SCREENS)
def test_screen(name: str) -> None:
    state, buttons = SCREENS[name]
    emu = emulator(state)
    tap(emu, buttons)
    emu.run_frames(SETTLE.get(name, 0))
    assert_matches_golden(emu, name)
