"""The fight's popup words in French: the sprite sheet at D9:0000 (S-DD1, 8 KB of 4bpp tiles; C0:23C3 DMAs it to VRAM
word 0x7000 with each map load and fights draw from it) redrawn, the stream moved (src/battle/popups.s).

The words sit on the sheet's tile row 14, each in its own run of tiles: Short (0-2) and Long (3-4), the range of the
special move on L / R, then Guard (5-7), Guts!! (8-10), Heal (11-12), MISS!! (13-15). A letter is ink on rows 1-6
(the top three in one colour, the bottom three in another, a pair per word) with a colour 1 outline on its four
sides. A word is wiped from its run and the French drawn from x 1 in the same colours; Long stays.

SKILL! (frame C8:84C4, a combat skill going off) is three tiles away from the row, 1A6 / 1CA / 1B6 left to right:
Talent!, kerned, fills their 24 px.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from tools import obj_letters as letters
from tools import sdd1
from tools.rom import ROOT

SHEET = 0xD90000
SIZE = 0x2000  # bytes the fight start DMAs
OUT = ROOT / "build" / "gen" / "battle_obj.bin"
ROW = 14  # tile row of the words
COLS = 16
OUTLINE = letters.OUTLINE

# fmt: off
GLYPHS: letters.Glyphs = {  # rows 1-6; lowercase from the sheet's own words, the rest drawn alike
    "C": (".##.", "#..#", "#...", "#...", "#..#", ".##."),
    "G": (".##.", "#..#", "#...", "#.##", "#..#", ".###"),
    "R": ("###.", "#..#", "#..#", "###.", "#.#.", "#..#"),
    "S": ("####", "#...", "####", "...#", "...#", "####"),
    "T": ("###", ".#.", ".#.", ".#.", ".#.", ".#."),
    "a": ("...", ".#.", "..#", ".##", "#.#", ".##"),
    "d": ("..#", "..#", ".##", "#.#", "#.#", ".##"),
    "e": ("...", ".#.", "#.#", "###", "#..", ".##"),
    "é": ("..#", ".#.", "#.#", "###", "#..", ".##"),
    "i": ("#", ".", "#", "#", "#", "#"),
    "l": ("#", "#", "#", "#", "#", "#"),
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
    tiles: tuple[int, ...]  # sheet tiles, left to right
    text: str
    top: int  # ink colour, rows 1-3
    bottom: int  # rows 4-6


def run(first: int, count: int) -> tuple[int, ...]:
    """`count` tiles from `first` on the words' row."""
    return tuple(range(ROW * COLS + first, ROW * COLS + first + count))


WORDS = (
    Word(run(0, 3), "Court", 11, 10),
    Word(run(5, 3), "Garde", 4, 3),
    Word(run(8, 3), "Cran!!", 15, 11),
    Word(run(11, 2), "Soin", 15, 4),
    Word(run(13, 3), "Raté!!", 15, 14),
    Word((0xA6, 0xCA, 0xB6), "Talent!", 15, 11),
)


def ink(text: str) -> list[list[bool]]:
    return letters.ink(text, GLYPHS)


def draw(data: bytearray, word: Word) -> None:
    grid = letters.paint(word.text, GLYPHS, len(word.tiles) * 8, word.top, word.bottom)
    for y, row in enumerate(grid):
        for x, colour in enumerate(row):
            letters.put(data, word.tiles[x // 8] * 32, x % 8, y, colour)


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
