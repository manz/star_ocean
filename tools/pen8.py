"""katsuji's sumi/8 for src/menu/pen8.s, the runtime 8x8 pen: names typed in game (party names and nicknames in
RAM) drawn proportionally like the baked vwf8 strings.

build/gen/pen8.i holds, per code below FIXED (the menu 8x8 table's letters), the glyph's 8 rows of 1bpp ink, left
aligned (`pen8_glyphs`), and its advance in pixels (`pen8_widths`, 0: sumi/8 does not draw it, the game does).
PEN8_MAGIC is a hash of both: a cache left in SRAM by another font is dropped.
"""

from __future__ import annotations

import zlib
from pathlib import Path

import numpy as np
from katsuji.fonts import bundled
from katsuji.remap import table_texts

from tools.encode_menus import TABLE
from tools.rom import ROOT
from tools.vwf8 import FIXED, SPACE

FONT = "sumi/8"
CODES = FIXED.start  # codes 0..CODES-1: letters, digits, punctuation


def glyphs() -> tuple[bytes, bytes]:
    """(8 rows per code, an advance per code), the space's advance included."""
    pixels = bundled(FONT).layout(table_texts(TABLE)).pixels
    rows, widths = bytearray(), bytearray()
    for code in range(CODES):
        cell = pixels[(code // 16) * 8 : (code // 16) * 8 + 8, (code % 16) * 8 : (code % 16) * 8 + 8] != 0
        rows.extend(int("".join("1" if v else "0" for v in row), 2) for row in cell)
        ink = np.flatnonzero(cell.any(axis=0))
        widths.append(int(ink[-1]) + 1 if ink.size else 0)
    return bytes(rows), bytes(widths)


def build(out: Path = ROOT / "build" / "gen") -> None:
    rows, widths = glyphs()

    def table(name: str, data: bytes) -> str:
        lines = ["    .db " + ", ".join(f"0x{b:02X}" for b in data[i : i + 16]) for i in range(0, len(data), 16)]
        return f".alloc {name} in text16 {{\n" + "\n".join(lines) + "\n}"

    asm = [
        f"PEN8_CODES := 0x{CODES:02X}",
        f"PEN8_SPACE := 0x{SPACE:02X}",
        f"PEN8_MAGIC := 0x{zlib.crc32(rows + widths) & 0xFFFF:04X}",
        table("pen8_glyphs", rows),
        table("pen8_widths", widths),
    ]
    (out / "pen8.i").write_text("\n".join(asm) + "\n", encoding="utf-8")
