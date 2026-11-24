"""The ending staff roll: the French lines pack into the game's container, the accented letters get glyphs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import ending_credits, sdd1
from tools.ending_credits import CENTRED, CONTINUED, Font, line_bytes
from tools.lz import decode
from tools.rom import DEFAULT_ROM, Rom

needs_rom = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


def _lines(packed: bytes) -> list[bytes]:
    data, _ = decode(lambda at, n: packed[at : at + n], 0)
    out, i = [], 0
    while i < len(data):
        j = data.index(0, i + 1)
        out.append(data[i:j])
        i = j + 1
    return out


@needs_rom
def test_the_roll_ends_with_the_end_code(tmp_path: Path) -> None:
    count = ending_credits.build(out=tmp_path)
    lines = _lines((tmp_path / "ending_credits.bin").read_bytes())
    assert (len(lines), lines[-1]) == (count + 1, bytes([ending_credits.END]))


@needs_rom
def test_an_accented_letter_takes_a_spare_code_and_a_new_glyph() -> None:
    font = Font(Rom())
    code = font.encode("é")[0]
    assert chr(code) in ending_credits.SPARE and font.map[code - 0x20] == ending_credits.GLYPH_COUNT


@needs_rom
def test_an_accent_is_drawn_above_its_letter() -> None:
    font = Font(Rom())
    plain, accented = font.glyph("e"), font.glyph("é")
    rows = [y for y in range(16) for x in range(8) if font.pixel(accented.tile, x, y)]
    assert accented.advance == plain.advance and min(rows) < 7


@needs_rom
def test_the_sheet_still_packs_into_its_dma_size() -> None:
    font = Font(Rom())
    font.encode("éèàçÉ")
    assert sdd1.decompress_bytes(sdd1.compress(bytes(font.sheet)), ending_credits.FONT_BYTES)[0] == bytes(font.sheet)


@needs_rom
def test_a_long_role_alone_starts_at_the_left() -> None:
    font = Font(Rom())
    (line,) = line_bytes(font, {"role": "Programmation des scènes"})
    assert 0 < line[0] < len("Programmation des scènes")


@needs_rom
def test_a_name_under_another_and_a_centred_line() -> None:
    font = Font(Rom())
    assert line_bytes(font, {"name": "PINKY"}) == [bytes([CONTINUED]) + b"  PINKY\0"]
    assert line_bytes(font, {"center": "STAFF"}) == [bytes([CENTRED]) + b"STAFF\0"]


@needs_rom
def test_a_line_past_the_screen_is_refused() -> None:
    with pytest.raises(ValueError, match="does not fit"):
        line_bytes(Font(Rom()), {"role": "Conception", "name": "YOSHIHARU GOTANDA YOSHIHARU GOTANDA"})
