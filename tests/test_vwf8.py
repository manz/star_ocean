"""The 8x8 strings the menu VWF uploads (tools/vwf8.py)."""

from __future__ import annotations

from script import Table

from tools.encode_menus import TABLE
from tools.vwf8 import CELL_END, CELL_NEWLINE, bake

_TABLE = Table(str(TABLE))


def _bake(text: str, anchored: bool = False) -> tuple[bytes, bytes]:
    baked = bake(_TABLE.to_bytes(text) + b"\xff", anchored)
    assert baked is not None
    return baked


def test_a_string_keeps_one_cell_per_character() -> None:
    _, cells = _bake("AppelLapin")
    assert len(cells) == len("AppelLapin") + 1


def test_a_proportional_name_shows_fewer_tiles_than_letters() -> None:
    tiles, _ = _bake("AppelLapin")
    assert len(tiles) // 16 < len("AppelLapin")


def test_the_cells_past_the_ink_are_blank() -> None:
    _, cells = _bake("AppelLapin")
    assert cells[-2] == 0


def test_the_cells_end_with_the_end_mark() -> None:
    _, cells = _bake("Arme")
    assert cells[-1] == CELL_END


def test_a_newline_becomes_a_newline_cell() -> None:
    _, cells = _bake("PV\nPM", anchored=True)
    assert cells[2] == CELL_NEWLINE


def test_an_anchored_word_starts_at_its_fixed_column() -> None:
    _, cells = _bake("PV      PM", anchored=True)
    assert cells[8] != 0


def test_identical_tiles_are_uploaded_once() -> None:
    tiles, _ = _bake("i      i", anchored=True)
    assert len(tiles) == 16


def test_a_two_row_kana_code_is_left_to_the_game() -> None:
    assert bake(bytes([0x41, 0xC0, 0xFF]), anchored=False) is None


def test_single_spaced_words_flow() -> None:
    _, cells = _bake("Choix d'un bloc")
    assert cells[len("Choix d'un bl")] == 0


def test_two_spaces_stop_at_the_fixed_column() -> None:
    _, cells = _bake("PV  PM")
    assert cells[4] != 0
