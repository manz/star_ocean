"""tools/pen8.py: sumi/8's glyphs for the runtime pen (src/menu/pen8.s)."""

from pathlib import Path

from katsuji.script import Table

from tools.encode_menus import TABLE
from tools.pen8 import CODES, build, glyphs


def test_a_glyph_is_8_rows_per_code() -> None:
    rows, widths = glyphs()
    assert (len(rows), len(widths)) == (8 * CODES, CODES)


def test_letters_have_an_advance() -> None:
    _, widths = glyphs()
    codes = Table(str(TABLE)).to_bytes("RatyIria")
    assert all(0 < widths[c] <= 8 for c in codes)


def test_the_include_holds_the_magic_and_both_tables(tmp_path: Path) -> None:
    build(out=tmp_path)
    text = (tmp_path / "pen8.i").read_text(encoding="utf-8")
    assert "PEN8_MAGIC :=" in text and "pen8_glyphs" in text and "pen8_widths" in text
