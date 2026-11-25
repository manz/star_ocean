"""The fight's popup words in French: the sprite sheet at D9:0000 (S-DD1, 8 KB of 4bpp tiles; C0:23C3 DMAs it to VRAM
word 0x7000 with each map load and fights draw from it) redrawn, the stream moved (src/battle/popups.s).

The words sit on the sheet's tile row 14, each in its own run of tiles: Short (0-2) and Long (3-4), the range of the
special move on L / R, then Guard (5-7), Guts!! (8-10), Heal (11-12), MISS!! (13-15). A letter is ink on rows 1-6
(the top three in one colour, the bottom three in another, a pair per word) with a colour 1 outline on its four
sides. A word is wiped from its run and the French drawn from x 1 in the same colours; Long stays.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from tools import sdd1
from tools.rom import ROOT

SHEET = 0xD90000
SIZE = 0x2000  # bytes the fight start DMAs
OUT = ROOT / "build" / "gen" / "battle_obj.bin"
ROW = 14  # tile row of the words
COLS = 16
OUTLINE = 1

# fmt: off
GLYPHS: dict[str, tuple[str, ...]] = {  # rows 1-6; lowercase from the sheet's own words, the rest drawn alike
    "C": (".##.", "#..#", "#...", "#...", "#..#", ".##."),
    "G": (".##.", "#..#", "#...", "#.##", "#..#", ".###"),
    "R": ("###.", "#..#", "#..#", "###.", "#.#.", "#..#"),
    "S": ("####", "#...", "####", "...#", "...#", "####"),
    "a": ("...", ".#.", "..#", ".##", "#.#", ".##"),
    "d": ("..#", "..#", ".##", "#.#", "#.#", ".##"),
    "e": ("...", ".#.", "#.#", "###", "#..", ".##"),
    "é": ("..#", ".#.", "#.#", "###", "#..", ".##"),
    "i": ("#", ".", "#", "#", "#", "#"),
    "n": ("...", "...", "##.", "#.#", "#.#", "#.#"),
    "o": ("...", "...", "###", "#.#", "#.#", "###"),
    "r": ("...", "...", "#.#", "##.", "#..", "#.."),
    "t": ("...", ".#.", "###", ".#.", ".#.", ".##"),
    "u": ("...", "...", "#.#", "#.#", "#.#", ".##"),
    "!": ("#", "#", "#", "#", ".", "#"),
}
# fmt: on


@dataclass(frozen=True)
class Word:
    first: int  # tile on the row
    tiles: int
    text: str
    top: int  # ink colour, rows 1-3
    bottom: int  # rows 4-6


WORDS = (
    Word(0, 3, "Court", 11, 10),
    Word(5, 3, "Garde", 4, 3),
    Word(8, 3, "Cran!!", 15, 11),
    Word(11, 2, "Soin", 15, 4),
    Word(13, 3, "Raté!!", 15, 14),
)


def _tile_offset(tile: int) -> int:
    return (ROW * COLS + tile) * 32


def _set(data: bytearray, tile: int, x: int, y: int, colour: int) -> None:
    off = _tile_offset(tile)
    bit = 7 - x
    for n, at in enumerate((off + y * 2, off + y * 2 + 1, off + 16 + y * 2, off + 16 + y * 2 + 1)):
        data[at] = data[at] & ~(1 << bit) | ((colour >> n) & 1) << bit


def ink(text: str) -> list[list[bool]]:
    """The word's ink, 8 rows (0 and 7 left for the outline), letters a column apart, from column 1."""
    rows = [[False] for _ in range(8)]
    for n, ch in enumerate(text):
        glyph = GLYPHS[ch]
        if n:
            for row in rows:
                row.append(False)
        for y in range(8):
            line = glyph[y - 1] if 1 <= y <= 6 else "." * len(glyph[0])
            rows[y].extend(c == "#" for c in line)
    return rows


def draw(data: bytearray, word: Word) -> None:
    width = word.tiles * 8
    mask = ink(word.text)
    if len(mask[0]) + 1 > width:
        raise ValueError(f"{word.text!r}: {len(mask[0]) + 1} px, its run holds {width}")
    for y in range(8):
        for x in range(width):
            here = x < len(mask[0]) and mask[y][x]
            near = any(
                0 <= x + dx < len(mask[0]) and 0 <= y + dy < 8 and mask[y + dy][x + dx]
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            colour = (word.top if y <= 3 else word.bottom) if here else OUTLINE if near else 0
            _set(data, word.first + x // 8, x % 8, y, colour)


def sheet() -> bytes:
    data = bytearray(sdd1.decompress(SHEET, SIZE)[0])
    for word in WORDS:
        draw(data, word)
    return bytes(data)


def build(out: Path = OUT) -> int:
    """Compressed size (src/battle/popups.s places the stream in the text16 pool)."""
    packed = sdd1.compress(sheet())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(packed)
    return len(packed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    print(f"{build(ap.parse_args().out)} bytes")


if __name__ == "__main__":
    main()
