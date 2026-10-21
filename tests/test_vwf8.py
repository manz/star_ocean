"""The 8x8 strings the menu VWF uploads (tools/vwf8.py)."""

from __future__ import annotations

import numpy as np
from script import Table

from tools.encode_menus import TABLE
from tools.vwf8 import CELL_END, CELL_NEWLINE, bake, line

_TABLE = Table(str(TABLE))


def _bake(text: str, anchored: bool = False, stops: tuple[int, ...] = ()) -> tuple[bytes, bytes]:
    baked = bake(_TABLE.to_bytes(text) + b"\xff", anchored, stops)
    assert baked is not None
    return baked


def test_a_string_stops_at_its_last_inked_cell() -> None:
    tiles, cells = _bake("AppelLapin")
    assert len(cells) == len(tiles) // 16 + 1


def test_a_proportional_name_shows_fewer_tiles_than_letters() -> None:
    tiles, _ = _bake("AppelLapin")
    assert len(tiles) // 16 < len("AppelLapin")


def test_the_last_cell_before_the_end_mark_is_inked() -> None:
    _, cells = _bake("AppelLapin")
    assert cells[-2] != 0


def test_spelled_out_trailing_spaces_are_kept() -> None:
    _, cells = _bake("Fin   ")
    assert cells[-4:-1] == bytes(3)


def test_a_blank_string_keeps_its_cells() -> None:
    _, cells = _bake("    ")
    assert cells == bytes(4) + bytes([CELL_END])


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
    assert len(cells) < len("Choix d'un bloc") + 1


def test_two_spaces_stop_at_the_fixed_column() -> None:
    _, cells = _bake("PV  PM")
    assert cells[4] != 0


def test_each_word_starts_at_its_stop() -> None:
    ink = np.flatnonzero(line(_TABLE.to_bytes("Achat Vente Fin"), False, (0, 4, 8)).any(axis=0))
    starts = [int(x) for x, before in zip(ink, np.r_[-2, ink[:-1]], strict=True) if x - before > 1]
    assert starts == [0, 32, 64]
