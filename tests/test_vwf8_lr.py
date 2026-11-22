"""The battle L/R window's special move names (tools/vwf8.py `lr_table`)."""

from __future__ import annotations

import pytest
from katsuji.script import Table

from tools.encode_menus import TABLE, wide_values
from tools.import_menus import id_list
from tools.rom import DEFAULT_ROM, ROOT, Rom
from tools.vwf8 import COMBO_FIRST, END, LR_FIRST, LR_PX, LR_TALENTS, NO_TALENT, lr_table, width

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


@pytest.fixture(scope="module")
def table() -> bytes:
    return lr_table(Rom(), ROOT / "text" / "fr")


def test_a_short_name_points_at_its_special_move(table: bytes) -> None:
    """Ratix's second L/R name (names8 "C.Aérien") is 空破斬, battle16 "Rafale"."""
    assert table[0x0BB9 - LR_FIRST] == 0x273B - COMBO_FIRST


def test_a_name_maps_exactly_when_it_fits_the_row(table: bytes) -> None:
    """A move whose battle16 name runs past LR_PX keeps its names8 string (NO_TALENT)."""
    encoded, _ = wide_values(Rom(), "battle16", Table(str(TABLE)), ROOT / "text" / "fr" / "battle16.xml")
    names = dict(zip(id_list(Rom(), "battle16"), encoded, strict=True))
    for first, talents in LR_TALENTS.items():
        for k, sid in enumerate(talents):
            fits = width(names[sid][: names[sid].index(END)]) <= LR_PX
            assert (table[first - LR_FIRST + k] != NO_TALENT) == fits, hex(sid)


def test_ids_outside_the_blocks_are_left_to_the_game(table: bytes) -> None:
    mapped = {first - LR_FIRST + k for first, talents in LR_TALENTS.items() for k in range(len(talents))}
    assert all(b == NO_TALENT for i, b in enumerate(table) if i not in mapped)
