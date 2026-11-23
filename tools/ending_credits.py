"""Pack the French ending staff roll (text/fr/ending_credits.toml) for src/dialog/ending_credits.s.

The roll (map 605, after the last story step) is ASCII lines in a C0:4C53 container (DE:D8F0, `ldy` / `lda` at
C0:66EC), unpacked to $7F:4000; C0:6740 draws one every 64 frames into a 2bpp buffer, its glyphs from a sheet the
S-DD1 stream DC:698A unpacks to $7F:0000 (`ldx` / `lda` at C0:66BB). A line is a count byte, its text, 0: the count
is how many characters are measured to place it (x = 0x70 - (width + 4), the role right-aligned to the name column);
bit 7 halves the width (255: centred on that column, not the screen); 254 ends the roll.

Characters map through C0:6996 (ASCII 0x20-0x7A to a glyph) to 5-byte records (advance, rows, columns, first sheet
tile as a word; the sheet is 16 tiles wide). The sheet has no accented letters: each one the text uses is drawn from
its base letter into a free pair of tiles, takes an ASCII code the roll never uses, and gets a record appended to a
copy of the table. src/dialog/ending_credits.s places the four binaries and repoints the code to them.
"""

from __future__ import annotations

import argparse
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from tools import sdd1
from tools.encode_text import container
from tools.rom import ROOT, Rom

FONT, FONT_BYTES = 0xDC698A, 0xE00  # the S-DD1 sheet the DMA at C0:66B0 unpacks
TEXT = 0xDED8F0  # the roll's container
CHAR_MAP, MAP_SIZE = 0xC06996, 0x7B - 0x20
GLYPHS, GLYPH_COUNT, RECORD = 0xC069F1, 0x4D, 5
SPARE = "#$%*+<>@[\\]^_`"  # codes the roll never prints: their glyphs are dropped duplicates
COLUMN = 0x70 - 4  # where a measured run ends: the roles' right edge, the centred lines' middle
SCREEN = 256
TILE, SHEET_COLUMNS, INK = 16, 16, 3
ROLE, CONTINUED, CENTRED, END = 0, 1, 0xFF, 0xFE

# accent strokes, (dx from the letter's middle, row, colour), rows above a lowercase letter (x-height at row 7)
MARKS: dict[str, list[tuple[int, int, int]]] = {
    "́": [(2, 3, 1), (1, 4, INK), (0, 5, INK)],  # acute
    "̀": [(-2, 3, 1), (-1, 4, INK), (0, 5, INK)],  # grave
    "̂": [(0, 3, INK), (-1, 4, INK), (1, 4, INK), (-2, 5, 2), (2, 5, 2)],  # circumflex
    "̈": [(-1, 4, INK), (1, 4, INK)],  # diaeresis
    "̧": [(0, 13, INK), (1, 14, INK), (0, 14, 1)],  # cedilla, under the letter
}
CAPITAL_LIFT = 3  # a capital's top is at row 3: its accent sits 3 rows higher


@dataclass(frozen=True)
class Glyph:
    advance: int
    rows: int
    columns: int
    tile: int

    def record(self) -> bytes:
        return bytes([self.advance, self.rows, self.columns]) + self.tile.to_bytes(2, "little")


class Font:
    """The roll's sheet, character map and glyph records, with accented letters added."""

    def __init__(self, rom: Rom) -> None:
        self.sheet = bytearray(sdd1.decompress(FONT, FONT_BYTES, rom)[0])
        self.map = bytearray(rom.read(CHAR_MAP, MAP_SIZE))
        raw = rom.read(GLYPHS, GLYPH_COUNT * RECORD)
        self.glyphs = [
            Glyph(raw[at], raw[at + 1], raw[at + 2], raw[at + 3] | raw[at + 4] << 8)
            for at in range(0, GLYPH_COUNT * RECORD, RECORD)
        ]
        self.codes: dict[str, int] = {chr(c): c for c in range(0x20, 0x7B) if chr(c) not in SPARE}
        self.spare = list(SPARE)

    def glyph(self, ch: str) -> Glyph:
        if ch not in self.codes:
            self.add(ch)
        return self.glyphs[self.map[self.codes[ch] - 0x20]]

    def width(self, text: str) -> int:
        return sum(self.glyph(ch).advance for ch in text)

    def encode(self, text: str) -> bytes:
        return bytes(self.codes[ch] if ch in self.codes else self._code(ch) for ch in text)

    def _code(self, ch: str) -> int:
        self.add(ch)
        return self.codes[ch]

    def add(self, ch: str) -> None:
        """An accented letter: its base letter's ink in a free tile pair, the accent drawn on it."""
        base, *marks = list(unicodedata.normalize("NFD", ch))
        if base not in self.codes or len(marks) != 1 or marks[0] not in MARKS or not self.spare:
            raise ValueError(f"the ending font cannot draw {ch!r}")
        source = self.glyph(base)
        if source.rows != 2 or any(self._ink(source.tile + c) for c in range(1, source.columns)):
            raise ValueError(f"{base!r}: one column of two tiles expected")
        tile = self._free_pair()
        for row in range(2):
            self.sheet[(tile + row * SHEET_COLUMNS) * TILE : (tile + row * SHEET_COLUMNS + 1) * TILE] = self.sheet[
                (source.tile + row * SHEET_COLUMNS) * TILE : (source.tile + row * SHEET_COLUMNS + 1) * TILE
            ]
        middle = self._middle(tile)
        lift = CAPITAL_LIFT if base.isupper() and marks[0] != "̧" else 0
        for dx, row, colour in MARKS[marks[0]]:
            self._plot(tile, middle + dx, row - lift, colour)
        code = ord(self.spare.pop(0))
        self.map[code - 0x20] = len(self.glyphs)
        self.glyphs.append(Glyph(source.advance, 2, 1, tile))
        self.codes[ch] = code

    def _used(self) -> set[int]:
        return {g.tile + r * SHEET_COLUMNS + c for g in self.glyphs for r in range(g.rows) for c in range(g.columns)}

    def _free_pair(self) -> int:
        used, tiles = self._used(), len(self.sheet) // TILE
        for t in range(tiles - SHEET_COLUMNS):
            if (
                t not in used
                and t + SHEET_COLUMNS not in used
                and not self._ink(t)
                and not self._ink(t + SHEET_COLUMNS)
            ):
                return t
        raise ValueError("the ending font sheet is full")

    def _ink(self, tile: int) -> bool:
        return any(self.sheet[tile * TILE : (tile + 1) * TILE])

    def pixel(self, tile: int, x: int, y: int) -> int:
        """The colour at (x, y) of the two-tile column from `tile`."""
        t = tile + (y // 8) * SHEET_COLUMNS
        lo, hi = self.sheet[t * TILE + (y % 8) * 2 : t * TILE + (y % 8) * 2 + 2]
        return (lo >> (7 - x) & 1) | (hi >> (7 - x) & 1) << 1

    def _plot(self, tile: int, x: int, y: int, colour: int) -> None:
        t = tile + (y // 8) * SHEET_COLUMNS
        at = t * TILE + (y % 8) * 2
        bit = 1 << (7 - x)
        self.sheet[at] = self.sheet[at] & ~bit | (bit if colour & 1 else 0)
        self.sheet[at + 1] = self.sheet[at + 1] & ~bit | (bit if colour & 2 else 0)

    def _middle(self, tile: int) -> int:
        """The middle column of the letter's dark ink."""
        xs = [x for x in range(8) for y in range(16) if self.pixel(tile, x, y) == INK]
        return (min(xs) + max(xs) + 1) // 2

    def table(self) -> bytes:
        return b"".join(g.record() for g in self.glyphs)


def line_bytes(font: Font, line: dict[str, object]) -> list[bytes]:
    """A TOML line's lines: centre, role (and name), name under the one above, or a run of blanks."""
    if "blank" in line:
        return [bytes([ROLE, 0])] * int(str(line["blank"]))
    if "center" in line:
        text = str(line["center"])
        _fits(font, text, COLUMN - font.width(text) // 2)
        return [bytes([CENTRED]) + font.encode(text) + b"\0"]
    if "role" in line:
        role, name = str(line["role"]), str(line.get("name", ""))
        text = role + (" " + name if name else "")
        count = len(role)
        while count and font.width(role[:count]) > COLUMN:  # a long role alone starts at the left, spilling right
            count -= 1
        _fits(font, text, COLUMN - font.width(text[:count]))
        return [bytes([count]) + font.encode(text) + b"\0"]
    name = " " * (2 + int(str(line.get("indent", 0)))) + str(line["name"])
    _fits(font, name, COLUMN - font.width(" "))
    return [bytes([CONTINUED]) + font.encode(name) + b"\0"]


def _fits(font: Font, text: str, x: int) -> None:
    if x < 0 or x + font.width(text) > SCREEN:
        raise ValueError(f"{text!r} does not fit the screen (x {x}, width {font.width(text)})")


def build(src: Path = ROOT / "text" / "fr" / "ending_credits.toml", out: Path = ROOT / "build" / "gen") -> int:
    """ending_credits.bin (the container), ending_font.bin (the S-DD1 sheet), ending_glyphs.bin (the records),
    ending_map.bin (the character map). Returns the line count."""
    font = Font(Rom())
    lines = [b for line in tomllib.loads(src.read_text(encoding="utf-8"))["lines"] for b in line_bytes(font, line)]
    out.mkdir(parents=True, exist_ok=True)
    (out / "ending_credits.bin").write_bytes(container(b"".join(lines) + bytes([END, 0])))
    (out / "ending_font.bin").write_bytes(sdd1.compress(bytes(font.sheet)))
    (out / "ending_glyphs.bin").write_bytes(font.table())
    (out / "ending_map.bin").write_bytes(bytes(font.map))
    return len(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} lines")


if __name__ == "__main__":
    main()
