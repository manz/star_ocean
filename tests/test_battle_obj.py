"""Fight popups: the French words fit their runs, only the words' tiles change, and the sheet compresses back."""

from __future__ import annotations

import pytest

from tools import battle_obj, sdd1
from tools.rom import DEFAULT_ROM

ROW_BYTES = battle_obj.COLS * 32
ROW_START = battle_obj.ROW * ROW_BYTES


def test_a_word_wider_than_its_run_is_refused() -> None:
    with pytest.raises(ValueError, match="its run holds"):
        battle_obj.draw(bytearray(battle_obj.SIZE), battle_obj.Word(0, 1, "Court", 15, 15))


def test_letters_sit_a_column_apart_from_column_one() -> None:
    assert ["".join("#" if v else "." for v in row) for row in battle_obj.ink("i!")] == [
        "....",
        ".#.#",
        "...#",
        ".#.#",
        ".#.#",
        ".#..",
        ".#.#",
        "....",
    ]


def test_a_word_is_outlined_in_colour_one() -> None:
    data = bytearray(battle_obj.SIZE)
    battle_obj.draw(data, battle_obj.Word(0, 1, "i", 15, 14))
    tile = data[ROW_START : ROW_START + 32]
    colours = {
        sum(((tile[(16 if n > 1 else 0) + y * 2 + n % 2] >> (7 - x)) & 1) << n for n in range(4))
        for y in range(8)
        for x in range(8)
    }
    assert colours == {0, battle_obj.OUTLINE, 15, 14}


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
def test_only_the_words_row_changes() -> None:
    old = sdd1.decompress(battle_obj.SHEET, battle_obj.SIZE)[0]
    new = battle_obj.sheet()
    assert old[:ROW_START] == new[:ROW_START]
    assert old[ROW_START + ROW_BYTES :] == new[ROW_START + ROW_BYTES :]


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
def test_the_sheet_compresses_back() -> None:
    sheet = battle_obj.sheet()
    assert sdd1.decompress_bytes(sdd1.compress(sheet), battle_obj.SIZE)[0][: battle_obj.SIZE] == sheet


def test_a_letter_kerns_into_the_previous_one_s_empty_corner() -> None:
    assert ["".join("#" if v else "." for v in row) for row in battle_obj.ink("ra")] == [
        ".......",
        ".......",
        ".....#.",
        ".#.#..#",
        ".##..##",
        ".#..#.#",
        ".#...##",
        ".......",
    ]
