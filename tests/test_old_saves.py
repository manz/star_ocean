"""8 KB Japanese .srm files load in the patched game (src/core/saves.s).

tests/saves/fantasyanime_<n>.srm: the four three-slot saves of https://fantasyanime.com/valhalla/starocean_saves.htm
(1: arrival in the past, Portmis, Otanim; 2: Astral, Parj Temple, Van; 3: Sylvalant, Astral, Parj Temple; 4: the
Time & Space Lab, Fargett, Seven Star Ruins). Each opens on the load screen from the title, then each slot loads.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.screens import assert_matches_golden, emulator, tap

SAVES = Path(__file__).parent / "saves"
TO_LOAD_SCREEN = "A,A,A"  # title_continue: Continue
SLOT = {1: "LEFT,LEFT", 2: "LEFT", 3: ""}  # the cursor starts on the last slot saved
LOADED = 600  # frames after "Oui" for the field to fade in


def _sram(save: int) -> bytes:
    return (SAVES / f"fantasyanime_{save}.srm").read_bytes()


@pytest.mark.parametrize("save", [1, 2, 3, 4])
def test_load_screen_lists_the_slots(save: int) -> None:
    emu = emulator("title_continue", _sram(save))
    tap(emu, TO_LOAD_SCREEN)
    assert_matches_golden(emu, f"old_save_{save}")


@pytest.mark.parametrize("slot", [1, 2, 3])
@pytest.mark.parametrize("save", [1, 2, 3, 4])
def test_slot_loads_into_the_game(save: int, slot: int) -> None:
    emu = emulator("title_continue", _sram(save))
    tap(emu, f"{TO_LOAD_SCREEN},{SLOT[slot]},A,A")
    emu.run_frames(LOADED)
    assert_matches_golden(emu, f"old_save_{save}_{slot}")
