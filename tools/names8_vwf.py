"""Bake the names8 strings (items, skills, spells, enemies) as proportional 8x8 strips for src/menu/vwf8.s.

Each string is composed with the 8x8 VWF font (fonts/8x8vwf.png, cells per text/so_8x8.tbl), kerned pair by pair,
drawn in the menu font's style (plane 1 = ink, colour 3; plane 0 = ink and its shadow one pixel right and down,
colour 1) and cut into 2bpp tiles, compressed as one S-DD1 stream: the menu DMAs it straight into VRAM. The table
is indexed by names8 position (the D7:0000 offset list): a 24-bit stream address and the tile count, 0 for a
string with no strip (the game draws it with the fixed font).
"""

from __future__ import annotations

import argparse
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
from katsuji import Atlas, VwfFont, pair_kerning, render

from tools import sdd1
from tools.encode_menus import NAMES8, french
from tools.import_menus import id_list
from tools.rom import ROOT, Rom

FONT = ROOT / "fonts" / "8x8vwf.png"
TABLE = ROOT / "text" / "so_8x8.tbl"
MAX_TILES = 8  # the item lists' name field
SPACE = 3
Strip = np.ndarray[tuple[int, int], np.dtype[np.uint8]]


@cache
def glyphs() -> dict[str, int]:
    out = {}
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        code, _, char = line.partition("=")
        if len(char) == 1:
            out[char] = int(code, 16)
    return out


@cache
def atlas() -> Atlas:
    return Atlas.open(FONT, 8, 8)


@cache
def font() -> VwfFont:
    return VwfFont.from_atlas(atlas())


def _kern(codes: list[int]) -> None:
    for pair in pairwise(codes):
        if pair not in font().kerning:
            value = pair_kerning(atlas(), *pair)
            if value < 0:
                font().kerning[pair] = -value


FOLD = {"É": "E", "È": "E", "Ê": "E", "Ë": "E", "Â": "A", "À": "A", "Ô": "O", "Ù": "U", "Ï": "I", "Î": "I", "Ç": "C"}


def fold(char: str) -> str:
    """The font's uppercase accents are blank (no room above the cap height): their base letter."""
    return FOLD[char] if char in FOLD and font().widths[glyphs()[char]] == 0 else char


def compose(text: str) -> Strip:
    """The text as ink (1) on an 8-row strip, space-separated runs kerned on their own."""
    parts: list[Strip] = []
    for n, word in enumerate(text.split(" ")):
        if n:
            parts.append(np.zeros((8, SPACE), np.uint8))
        codes = [glyphs()[fold(c)] for c in word]
        if codes:
            _kern(codes)
            parts.append(render(font(), codes))
    return np.concatenate(parts, axis=1) if parts else np.zeros((8, 0), np.uint8)


def tiles(ink: Strip) -> bytes:
    """2bpp tiles of the strip with the menu font's shadow."""
    width = -(-(ink.shape[1] + 1) // 8) * 8
    a = np.zeros((9, width + 1), np.uint8)
    a[:8, : ink.shape[1]] = ink
    shadow = a | np.roll(a, 1, 1) | np.roll(a, 1, 0) | np.roll(np.roll(a, 1, 0), 1, 1)
    out = bytearray()
    for t in range(width // 8):
        for y in range(8):
            row = slice(t * 8, t * 8 + 8)
            out.append(int("".join(map(str, shadow[y, row])), 2))
            out.append(int("".join(map(str, a[y, row])), 2))
    return bytes(out)


def strip(text: str) -> bytes | None:
    """The string's tiles, or None when the font lacks a glyph or it overflows the field."""
    if not text or any(c != " " and c not in glyphs() for c in text):
        return None
    data = tiles(compose(text))
    return data if len(data) <= MAX_TILES * 16 else None


def build(source: Path = ROOT / "text" / "fr" / "names8.xml", out: Path = ROOT / "build" / "gen") -> int:
    """names8_vwf_N.bin per distinct strip and names8_vwf.i (streams in text16, the table)."""
    strings = french(source)
    streams: dict[bytes, str] = {}
    asm, table = [], []
    for sid in id_list(Rom(), NAMES8.name):
        data = strip(strings.get(sid, ""))
        if data is None:
            table.append("    .dl 0\n    .db 0")
            continue
        if data not in streams:
            streams[data] = name = f"names8_vwf_{len(streams)}"
            (out / f"{name}.bin").write_bytes(sdd1.compress(data))
            asm.append(f'.alloc {name} in text16 {{\n    .incbin "{name}.bin"\n}}')
        table.append(f"    .dl {streams[data]}\n    .db {len(data) // 16}")
    asm.append(".alloc names8_vwf in text16 {\n" + "\n".join(table) + "\n}")
    (out / "names8_vwf.i").write_text("\n".join(asm) + "\n")
    return len(streams)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} strips")


if __name__ == "__main__":
    main()
