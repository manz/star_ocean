"""Title menu: the French items fit the sheet's cels and show from power on (the starfield and the cursor's
pulse differ from one power on to the next, so no golden picture)."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.screens import power_on, tap
from tools import sdd1, title_menu
from tools.rom import DEFAULT_ROM, ROOT

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")

TITLE = 1200  # power on to the title
MENU = 200  # after START
SHEET_VRAM = 0x7000  # the word CC:2441 sends the sheet to


def test_the_items_take_every_freed_cel(tmp_path: Path) -> None:
    assert title_menu.build(out=tmp_path) == len(title_menu.SLOTS)


def test_the_sheet_compresses_back_to_its_size(tmp_path: Path) -> None:
    title_menu.build(out=tmp_path)
    data, _ = sdd1.decompress_bytes((tmp_path / "title_sheet.bin").read_bytes(), title_menu.SHEET_BYTES)
    assert len(data) == title_menu.SHEET_BYTES


def test_an_item_too_long_for_the_sheet_is_refused(tmp_path: Path) -> None:
    src = tmp_path / "menu.toml"
    item = '[[item]]\nentry = 0xCC2BD0\ntext = "Nouvelle partie Nouvelle partie"\n'
    src.write_text(item * 2)
    with pytest.raises(ValueError, match="cels"):
        title_menu.build(src, tmp_path)


def test_power_on_loads_the_french_sheet() -> None:
    emu = power_on(TITLE)
    built = (ROOT / "build" / "gen" / "title_sheet.bin").read_bytes()
    sheet, _ = sdd1.decompress_bytes(built, title_menu.SHEET_BYTES)
    assert bytes(emu.vram_read_range(SHEET_VRAM * 2, title_menu.SHEET_BYTES)) == sheet


def test_the_menu_sprites_are_the_french_cels() -> None:
    emu = power_on(TITLE)
    tap(emu, "START")
    emu.run_frames(MENU)
    oam = bytes(emu.oam_read_range())
    tiles = {oam[i * 4 + 2] | (oam[i * 4 + 3] & 1) << 8 for i in range(128) if oam[i * 4 + 1] < 0xE0}
    assert set(title_menu.SLOTS) <= tiles
