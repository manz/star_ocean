"""menu16 strings against the 16x16 description box: the printer clears LINES lines, a longer text leaves its
last line on the screen below (the window border, the next description)."""

from __future__ import annotations

from pathlib import Path

import pytest
from katsuji.script import Table

from tools.encode_menus import wide_values
from tools.import_menus import id_list
from tools.menu_font16 import BASE, DIALOG_BASE, GEN, LINES, TABLE, lines, table_lines
from tools.rom import DEFAULT_ROM, ROOT, Rom

WIDTHS = GEN / "menu_font16_widths.bin"

pytestmark = pytest.mark.skipif(
    not DEFAULT_ROM.exists() or not WIDTHS.exists(), reason="base ROM or build/gen 16x16 font not present"
)


def test_a_space_breaks_the_line_past_its_width() -> None:
    widths = bytes([7] * 0x80)
    assert lines(bytes([0x11] * 20 + [0x10] + [0x11] * 9 + [0xFF]), widths) == 2


def test_every_menu16_string_fits_the_box() -> None:
    rom = Rom()
    encoded, _ = wide_values(rom, "menu16", Table(str(TABLE)), ROOT / "text" / "fr" / "menu16.xml")
    widths = WIDTHS.read_bytes()
    over = [
        f"{sid:04X}" for sid, value in zip(id_list(rom, "menu16"), encoded, strict=True) if lines(value, widths) > LINES
    ]
    assert over == []


def test_a_wide_glyph_keeps_its_run_of_codes(tmp_path: Path) -> None:
    table = tmp_path / "dialog.tbl"
    table.write_text("5078=œ\n", encoding="utf-8")
    moved = BASE - DIALOG_BASE
    assert f"{0x50 + moved:02X}{0x78 + moved:02X}=œ" in table_lines(table)
