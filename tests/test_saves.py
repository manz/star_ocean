"""Saves at the start of SRAM (src/core/saves.s): every moved operand, and a save made in game."""

from __future__ import annotations

import re

import pytest

from tests.screens import emulator, tap
from tools.rom import DEFAULT_ROM, ROOT, Rom

SITES = [
    (int(site, 16), int(old, 16))
    for site, old in re.findall(r"^move\(0x(\w+), 0x(\w+)\)", (ROOT / "src/core/saves.s").read_text(), re.MULTILINE)
]
SAVES_END = 0x701E6B  # slots 0x700000-0x701DFF, system bytes to 0x701E6A
OURS = range(0xC06B72, 0xC07000)  # code_c0: the SRAM text routines
SAVE_SLOT_2 = "A,A,A,X,RIGHT,RIGHT,RIGHT,DOWN,A,RIGHT,A,A"  # menu > Sauver > slot 2 > Oui


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
def test_every_site_names_the_old_save_area() -> None:
    rom = Rom()
    wrong = [hex(site) for site, old in SITES if int.from_bytes(rom.read(site + 1, 2), "little") != old]
    assert (len(SITES), wrong) == (120, [])


def _save_slot_2() -> tuple[bytes, set[int]]:
    emu = emulator("load_screen")
    strays: set[int] = set()

    def note(address: int, _value: int) -> None:
        pc = emu.get_state().pc & 0xFFFFFF
        if address >= SAVES_END and pc not in OURS:
            strays.add(pc)

    emu.add_read_callback(SAVES_END, 0x707FFF, note)
    emu.add_write_callback(SAVES_END, 0x707FFF, note)
    tap(emu, SAVE_SLOT_2)
    emu.run_frames(120)
    return bytes(emu.read_range(0x700A00, 1)), strays


def test_a_save_lands_in_its_new_slot() -> None:
    assert _save_slot_2()[0] == b"\x1d"  # the slot's first byte, written by C2:CF15


def test_the_game_leaves_sram_past_the_saves_alone() -> None:
    assert _save_slot_2()[1] == set()
