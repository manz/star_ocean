"""Bake the 8x8 menu strings (labels8, names8) as proportional tiles for src/menu/vwf8.s.

Glyphs are the menu font's own (fonts/so_menu8.png, tile = string byte), trimmed to their inked columns and set
GAP apart; codes in FIXED (icons, words drawn across tiles) keep their 8 px. A string keeps
its cells: names8 runs proportional then pads with blanks to its length, labels8 puts each word at the column it had
in fixed width (menus line them up with cursors and with numbers drawn below). Each string's non-blank tiles are one S-DD1 stream; its
record says which tile each cell shows:

    .dl stream (0: no tiles)
    .db tiles
    .db cell... : 0 blank, n the stream's tile n, NEWLINE, END

`vwf8_keys` sorts the records by the string's address (encode_menus.place): 8 bytes each, address word, bank, 0,
record pointer, 0. Strings with a code the writer draws over two rows (C0+) have no record: the game draws them.
"""

from __future__ import annotations

import argparse
from functools import cache
from pathlib import Path

import numpy as np
from PIL import Image
from script import Table

from tools import sdd1
from tools.encode_menus import LABELS8, NAMES8, TABLE, SmallDb, place, values
from tools.menu_font import PNG
from tools.rom import ROOT, Rom

SPACE, NEWLINE, END = 0xBF, 0xFC, 0xFF
CELL_NEWLINE, CELL_END = 0xFE, 0xFF
FIXED = range(0xA0, 0xBF)  # icons, words drawn across tiles
SPACE_PX = 3
GAP = 1  # after a glyph's shadow column
Pixels = np.ndarray[tuple[int, int], np.dtype[np.uint8]]


@cache
def font() -> Pixels:
    return ((np.asarray(Image.open(PNG).convert("L"), np.uint16) + 42) // 85).astype(np.uint8)


@cache
def glyph(code: int) -> Pixels:
    """The code's tile, trimmed to its inked columns unless it is fixed."""
    tile = font()[code // 16 * 8 : code // 16 * 8 + 8, code % 16 * 8 : code % 16 * 8 + 8]
    if code in FIXED:
        return tile
    inked = np.flatnonzero(tile.any(axis=0))
    return tile[:, inked[0] : inked[-1] + 1] if inked.size else tile[:, :0]


def run(codes: bytes) -> Pixels:
    """A word set proportionally."""
    out = np.zeros((8, 8 * len(codes) + 8), np.uint8)
    x = 0
    for code in codes:
        g = glyph(code)
        out[:, x : x + g.shape[1]] = np.maximum(out[:, x : x + g.shape[1]], g)
        x += g.shape[1] + GAP
    return out[:, : max(x - GAP, 0)]


def line(codes: bytes, anchored: bool) -> Pixels:
    """One line over its cells: words at their fixed-width column, or flowing with SPACE_PX spaces."""
    out = np.zeros((8, 8 * len(codes) + 8), np.uint8)
    x = column = 0
    for word in codes.split(bytes([SPACE])):
        if word:
            start = 8 * column if anchored else x
            pixels = run(word)
            out[:, start : start + pixels.shape[1]] = pixels
            x = start + pixels.shape[1] + SPACE_PX
        else:
            x += SPACE_PX
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
    db: SmallDb
    for db, anchored in ((LABELS8, True), (NAMES8, False)):
        for value, address in place(db, values(rom, db, table, source / f"{db.name}.xml")).items():
            baked = bake(value, anchored)
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
