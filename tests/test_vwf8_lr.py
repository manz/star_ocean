"""The battle L/R window's special move names (tools/vwf8.py `lr_table`)."""

from __future__ import annotations

import pytest

from tools.rom import DEFAULT_ROM, ROOT, Rom
from tools.vwf8 import COMBO_FIRST, LR_FIRST, LR_TALENTS, NO_TALENT, lr_table

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


@pytest.fixture(scope="module")
def table() -> bytes:
    return lr_table(Rom(), ROOT / "text" / "fr")


def test_a_short_name_points_at_its_special_move(table: bytes) -> None:
    """Ratix's second L/R name (names8 "C.Aérien") is 空破斬, battle16 "Rafale"."""
    assert table[0x0BB9 - LR_FIRST] == 0x273B - COMBO_FIRST


def test_a_name_past_the_row_keeps_its_names8_string(table: bytes) -> None:
    """Fear's "Souffle du dieu de la Galaxie" (117 px) stays "SouffleDG"."""
    assert table[0x0D1D - LR_FIRST] == NO_TALENT


def test_ids_outside_the_blocks_are_left_to_the_game(table: bytes) -> None:
    mapped = {first - LR_FIRST + k for first, talents in LR_TALENTS.items() for k in range(len(talents))}
    assert all(b == NO_TALENT for i, b in enumerate(table) if i not in mapped)
