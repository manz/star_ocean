"""Bake the 8x8 menu strings (labels8, names8) as proportional tiles for src/menu/vwf8.s.

Glyphs are the menu font's own (fonts/so_menu8.png, tile = string byte) set by katsuji's auto mode (widths from the
ink, each pair kerned on the glyphs, shadow kept), or FF4's 8x8 VWF font with the menu font's shadow added (`FF4`);
codes in FIXED (icons, words drawn across tiles) keep their whole tile. A string keeps its cells: words run
proportional, SPACE_PX apart, then blanks pad it to its length; a word after two spaces or more starts at the column
it had in fixed width, every word of a COLUMNS string does (menus line those up with cursors and with numbers drawn
below). Each string's non-blank tiles are one S-DD1 stream; its record says which tile each cell shows:

    .dl stream (0: no tiles)
    .db tiles
    .db cell... : 0 blank, n the stream's tile n, NEWLINE, END

`vwf8_keys` sorts the records by the string's address (encode_menus.place): 8 bytes each, address word, bank, 0,
record pointer, 0. Strings with a code the writer draws over two rows (C0+) have no record: the game draws them.
"""

from __future__ import annotations

import argparse
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
from katsuji import Atlas, VwfFont, autohint, pair_kerning, render
from script import Table

from tools import sdd1
from tools.encode_menus import LABELS8, NAMES8, TABLE, place, values
from tools.import_menus import id_list
from tools.menu_font import PNG
from tools.rom import ROOT, Rom

SPACE, NEWLINE, END = 0xBF, 0xFC, 0xFF
CELL_NEWLINE, CELL_END = 0xFE, 0xFF
FIXED = range(0xA0, 0xBF)  # icons, words drawn across tiles
SPACE_PX = 3
# labels8 laid out in columns a single space apart (cursor stops, headers over numbers, the name entry's grid):
# every word at its fixed-width column.
COLUMNS = {0xEA6A, 0xEA6B, 0xEA74, 0xEA93, 0xEAD2, 0xEAD3, 0xEBDC, 0xECA9, *range(0xF6E0, 0xF6F7), 0xF712}
GAP = 1  # between runs and whole tiles
FF4 = False  # FF4's 8x8 VWF font (fonts/8x8vwf.png, 1bpp) with the menu font's shadow, instead of the menu font
FF4_FONT, FF4_TABLE = ROOT / "fonts" / "8x8vwf.png", ROOT / "text" / "so_8x8.tbl"
FOLD = {"É": "E", "È": "E", "Ê": "E", "Ë": "E", "Â": "A", "À": "A", "Ô": "O", "Ù": "U", "Ï": "I", "Î": "I", "Ç": "C"}
Pixels = np.ndarray[tuple[int, int], np.dtype[np.uint8]]


def _table(path: Path) -> dict[int, str]:
    out = {}
    for entry in path.read_text(encoding="utf-8").splitlines():
        code, _, char = entry.partition("=")
        if len(char) == 1:
            out[int(code, 16)] = char
    return out


@cache
def menu_atlas() -> Atlas:
    """The menu font: its grey levels are the colours 0-3."""
    atlas = Atlas.open(PNG, 8, 8)
    if atlas.colours is None or atlas.colours.max() != 3:
        raise ValueError(f"{PNG.name}: expected 4 grey levels")
    return atlas


def glyph(code: int) -> Pixels:
    """The code's whole menu font tile."""
    return menu_atlas().glyph_colours(code)


def menu_run(codes: list[int]) -> Pixels:
    """Menu font glyphs set by katsuji's auto mode: ink widths, each pair kerned on the glyphs, shadow kept."""
    return autohint(menu_atlas(), codes)


@cache
def ff4_atlas() -> Atlas:
    return Atlas.open(FF4_FONT, 8, 8)


@cache
def ff4_font() -> VwfFont:
    return VwfFont.from_atlas(ff4_atlas())


@cache
def ff4_code(code: int) -> int | None:
    """The FF4 font cell for a menu code, uppercase accents (blank there) folded to their letter."""
    cells = {char: cell for cell, char in _table(FF4_TABLE).items()}
    char = _table(TABLE).get(code)
    if char is None or code in FIXED or char not in cells:
        return None
    if char in FOLD and ff4_font().widths[cells[char]] == 0:
        char = FOLD[char]
    return cells.get(char)


def ff4_run(cells: list[int]) -> Pixels:
    """FF4 glyphs kerned pair by pair, shadowed right and down: ink 3, shadow 1."""
    for left, right in pairwise(cells):
        if (left, right) not in ff4_font().kerning and (value := pair_kerning(ff4_atlas(), left, right)) < 0:
            ff4_font().kerning[left, right] = -value
    ink = render(ff4_font(), cells).astype(np.uint8)
    a = np.zeros((9, ink.shape[1] + 1), np.uint8)
    a[:8, : ink.shape[1]] = ink
    shadow = a | np.roll(a, 1, 1) | np.roll(a, 1, 0) | np.roll(np.roll(a, 1, 0), 1, 1)
    out: Pixels = (shadow + 2 * a)[:8]
    return out


def _pieces(codes: bytes) -> list[Pixels]:
    """The word as kerned runs, FIXED codes (and, with FF4, codes its font lacks) as whole menu tiles."""
    out: list[Pixels] = []
    cells: list[int] = []
    for code in codes:
        cell = ff4_code(code) if FF4 else (None if code in FIXED else code)
        if cell is not None:
            cells.append(cell)
            continue
        if cells:
            out.append(ff4_run(cells) if FF4 else menu_run(cells))
            cells = []
        out.append(glyph(code))
    if cells:
        out.append(ff4_run(cells) if FF4 else menu_run(cells))
    return out


def run(codes: bytes) -> Pixels:
    """A word set proportionally."""
    out = np.zeros((8, 8 * len(codes) + 16), np.uint8)
    x = 0
    for g in _pieces(codes):
        out[:, x : x + g.shape[1]] = np.maximum(out[:, x : x + g.shape[1]], g)
        x += g.shape[1] + GAP
    return out[:, : max(x - GAP, 0)]


def line(codes: bytes, anchored: bool) -> Pixels:
    """One line over its cells: words flow SPACE_PX apart, and start at their fixed-width column after two spaces or
    more (a column stop), or always when `anchored`."""
    out = np.zeros((8, 8 * len(codes) + 8), np.uint8)
    x = column = spaces = 0
    for word in codes.split(bytes([SPACE])):
        if word:
            start = max(x, 8 * column) if anchored or spaces > 1 else x
            pixels = run(word)
            out[:, start : start + pixels.shape[1]] = pixels
            x = start + pixels.shape[1] + SPACE_PX
            spaces = 1
        else:
            x += SPACE_PX
            spaces += 1
        column += len(word) + 1
    return out[:, : 8 * len(codes)]


def planar(tile: Pixels) -> bytes:
    out = bytearray()
    for row in tile:
        out.append(int("".join(str(v & 1) for v in row), 2))
        out.append(int("".join(str(v >> 1) for v in row), 2))
    return bytes(out)


def bake(value: bytes, anchored: bool) -> tuple[bytes, bytes] | None:
    """(tiles, cells) of a terminated string, or None when the game must draw it."""
    body = value[: value.index(END)]
    if any(code >= 0xC0 and code != NEWLINE for code in body):
        return None
    tiles: dict[bytes, int] = {}
    cells = bytearray()
    for n, codes in enumerate(body.split(bytes([NEWLINE]))):
        if n:
            cells.append(CELL_NEWLINE)
        pixels = line(codes, anchored)
        for cell in range(len(codes)):
            tile = pixels[:, 8 * cell : 8 * cell + 8]
            cells.append(tiles.setdefault(planar(tile), len(tiles) + 1) if tile.any() else 0)
    cells.append(CELL_END)
    if len(tiles) >= CELL_NEWLINE:
        return None
    return b"".join(tiles), bytes(cells)


def records(rom: Rom, source: Path) -> list[tuple[int, bytes, bytes]]:
    """(address, tiles, cells) of every baked string, by address."""
    table = Table(str(TABLE))
    out = []
    for db in (LABELS8, NAMES8):
        encoded = values(rom, db, table, source / f"{db.name}.xml")
        columns = {value for sid, value in zip(id_list(rom, db.name), encoded, strict=True) if sid in COLUMNS}
        for value, address in place(db, encoded).items():
            baked = bake(value, value in columns)
            if baked:
                out.append((address, *baked))
    return sorted(out)


def build(source: Path = ROOT / "text" / "fr", out: Path = ROOT / "build" / "gen") -> int:
    """vwf8_N.bin per distinct tile run and vwf8.i (streams, records, keys in text16)."""
    baked = records(Rom(), source)
    streams: dict[bytes, str] = {}
    asm = [f"VWF8_RECORDS := {len(baked)}"]
    keys = []
    for n, (address, tiles, cells) in enumerate(baked):
        stream = "0"
        if tiles:
            if tiles not in streams:
                streams[tiles] = stream = f"vwf8_stream_{len(streams)}"
                (out / f"{stream}.bin").write_bytes(sdd1.compress(tiles))
                asm.append(f'.alloc {stream} in text16 {{\n    .incbin "{stream}.bin"\n}}')
            stream = streams[tiles]
        data = ", ".join(f"0x{b:02X}" for b in cells)
        asm.append(f".alloc vwf8_record_{n} in text16 {{\n    .dl {stream}\n    .db {len(tiles) // 16}, {data}\n}}")
        keys.append(
            f"    .dw 0x{address & 0xFFFF:04X}\n    .db 0x{address >> 16:02X}, 0\n    .dl vwf8_record_{n}\n    .db 0"
        )
    asm.append(".alloc vwf8_keys in text16 {\n" + "\n".join(keys) + "\n}")
    for old in out.glob("names8_vwf*"):
        old.unlink()
    (out / "vwf8.i").write_text("\n".join(asm) + "\n")
    return len(baked)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} records")


if __name__ == "__main__":
    main()
