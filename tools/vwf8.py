"""Bake the 8x8 menu strings (labels8, names8) as proportional tiles for src/menu/vwf8.s.

Glyphs are the menu font's own (fonts/so_menu8.png, tile = string byte) as 1bpp ink, set by katsuji's auto mode
(widths from the ink, each pair kerned on the glyphs), or FF4's 8x8 VWF font (`FF4`); the run then gets the shadow
the menu font draws its letters with; codes in FIXED (icons, words drawn across tiles) keep their whole tile. A
string keeps its cells: words run proportional, SPACE_PX apart, up to its last inked tile and the trailing spaces it
spells out (the game's text only drew its own characters: padding to the fixed-width length ran over window borders);
a word after two spaces or more starts at the column it had in fixed width, every word of a COLUMNS string does
(menus line those up with cursors and with numbers drawn below), or at its STOPS column. Each string's non-blank tiles are one S-DD1 stream; its record says which tile each cell shows:

    .dl stream (0: no tiles)
    .db tiles
    .db cell... : 0 blank, n the stream's tile n, NEWLINE, END

`vwf8_keys` sorts the records by the string's address (encode_menus.place): 8 bytes each, address word, bank, 0,
record pointer, 0. Strings with a code the writer draws over two rows (C0+) have no record: the game draws them.
`vwf8_combos` holds, per special move id from COMBO_FIRST, its battle16 name's record (.dl, then 0; 0: none) for the
Talents combo slots and list (src/menu/vwf8.s), wrapped onto the slot's second row past COMBO_PX, then the list's
"(Vide)" (COMBO_EMPTY). `vwf8_lr` gives, per names8 id from LR_FIRST
(the battle's L/R window: a block of 0x20 per character), the combo position whose record the fight draws instead
(0xFF: the names8 string stays), for names that fit LR_PX on one row.
"""

from __future__ import annotations

import argparse
from functools import cache
from itertools import pairwise
from pathlib import Path

import numpy as np
from katsuji import Atlas, VwfFont, pair_kerning, render
from katsuji.script import Table

from tools import sdd1
from tools.encode_menus import LABELS8, NAMES8, TABLE, place, values, wide_values
from tools.import_menus import id_list
from tools.menu_font import PNG
from tools.rom import ROOT, Rom

SPACE, NEWLINE, END = 0xBF, 0xFC, 0xFF
CELL_NEWLINE, CELL_END = 0xFE, 0xFF
FIXED = range(0xA0, 0xBF)  # icons, words drawn across tiles
SPACE_PX = 3
# labels8 laid out in columns a single space apart (cursor stops, headers over numbers, the name entry's grid):
# every word at its fixed-width column.
COLUMNS = {0xEA6A, 0xEA6B, 0xEA74, 0xEA93, 0xEBDC, 0xECA9, *range(0xF6E0, 0xF6F7), 0xF712}
# Cursor stops whose French words outgrow the Japanese columns: each word at its cell.
STOPS = {0xEAD0: (0, 5), 0xEAD2: (0, 5, 10), 0xEAD3: (0, 5, 10)}  # shop tabs: src/menu/layout8.s moves the hand
GAP = 1  # between runs and whole tiles
COMBO_FIRST, COMBO_COUNT = 0x2710, 0x82  # special moves, by battle16 id
COMBO_PX = 96  # a combo slot's row: 12 cells
COMBO_EMPTY = 0xEA74  # menu16 "(Vide)": the Talents list's first row, after the special moves in vwf8_combos
LR_FIRST, LR_COUNT = 0x0BB8, 0x180  # names8 ids of the battle L/R window's special moves, 0x20 a character
LR_PX = 80  # the L/R window's name row: 10 cells (src/battle/windows.s)
# Each character's L/R names8 block, in order, as battle16 special move ids (matched on the Japanese names8 kana).
LR_TALENTS = {
    0x0BB8: (
        0x273A,
        0x273B,
        0x273C,
        0x273D,
        0x273E,
        0x273F,
        0x2740,
        0x2741,
        0x2742,
        0x2743,
        0x2744,
        0x2745,
        0x2749,
        0x274A,
        0x274B,
        0x274C,
    ),
    0x0C38: (0x2765, 0x2766, 0x2767, 0x2768, 0x276B, 0x276C, 0x276D, 0x276E, 0x276F, 0x2770),
    0x0C58: (0x273A, 0x273C, 0x273D, 0x273E, 0x273F, 0x2740, 0x274F, 0x2750, 0x2751, 0x2743, 0x2752, 0x2745),
    0x0C98: (0x2786, 0x2788, 0x2789, 0x278A, 0x278B, 0x278C, 0x278E, 0x2790, 0x276F),
    0x0CB8: (0x2771, 0x2772, 0x2773, 0x2774, 0x2775, 0x2776, 0x2777, 0x2778, 0x2779, 0x2791),
    0x0CD8: (0x273A, 0x273C, 0x273E, 0x273F, 0x2740, 0x2741, 0x2742, 0x2743, 0x2745),
    0x0CF8: (0x277A, 0x277B, 0x277C, 0x277D, 0x277E, 0x277F, 0x2780, 0x2781, 0x2782, 0x2783, 0x2784, 0x2785),
    0x0D18: (0x2753, 0x2754, 0x2755, 0x2756, 0x2760, 0x2761, 0x2762, 0x2763, 0x2764),
}
NO_TALENT = 0xFF
INK, SHADOW = 3, 1  # the menu font's letter colours
FF4 = True  # FF4's 8x8 VWF font (fonts/8x8vwf.png, 1bpp) instead of the menu font's letters
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


@cache
def menu_ink() -> Atlas:
    """The menu font as 1bpp: its letters' ink colour, shadow left out."""
    return menu_atlas().ink_only([INK])


@cache
def menu_font() -> VwfFont:
    return VwfFont.from_atlas(menu_ink())


def menu_run(codes: list[int]) -> Pixels:
    """Menu font letters kerned on their ink (katsuji's auto mode), then shadowed as the font draws them."""
    return shadowed(kerned(menu_font(), menu_ink(), codes))


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
    """FF4 glyphs kerned pair by pair, shadowed as the menu font draws its letters."""
    return shadowed(kerned(ff4_font(), ff4_atlas(), cells))


def kerned(font: VwfFont, atlas: Atlas, codes: list[int]) -> Pixels:
    """The 1bpp ink of `codes`, each pair kerned on the glyphs the first time it shows up."""
    for left, right in pairwise(codes):
        if (left, right) not in font.kerning and (value := pair_kerning(atlas, left, right)) < 0:
            font.kerning[left, right] = -value
    out: Pixels = render(font, codes).astype(np.uint8)
    return out


def shadowed(ink: Pixels) -> Pixels:
    """Ink as colour INK with a SHADOW one pixel right, down and diagonally, as the menu font's letters."""
    a = np.zeros((9, ink.shape[1] + 1), np.uint8)
    a[:8, : ink.shape[1]] = ink
    shadow = a | np.roll(a, 1, 1) | np.roll(a, 1, 0) | np.roll(np.roll(a, 1, 0), 1, 1)
    out: Pixels = np.where(a != 0, INK, np.where(shadow != 0, SHADOW, 0)).astype(np.uint8)[:8]
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


def line(codes: bytes, anchored: bool, stops: tuple[int, ...] = ()) -> Pixels:
    """One line over its cells: words flow SPACE_PX apart, and start at their fixed-width column after two spaces or
    more (a column stop), or always when `anchored`; the nth word at the nth of `stops` instead."""
    out = np.zeros((8, 8 * len(codes) + 8), np.uint8)
    x = column = spaces = words = 0
    for word in codes.split(bytes([SPACE])):
        if word:
            if words < len(stops):
                start = max(x, 8 * stops[words])
            else:
                start = max(x, 8 * column) if anchored or spaces > 1 else x
            words += 1
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


def _trimmed(row: list[int], spaces: int) -> list[int]:
    """A line's cells without the blanks the proportional text freed at its end (they ran over window borders),
    keeping the trailing spaces the string spells out (blank strings erase a field)."""
    end = len(row)
    while end and row[end - 1] == 0:
        end -= 1
    return row[: min(len(row), end + spaces)]


def bake(value: bytes, anchored: bool, stops: tuple[int, ...] = ()) -> tuple[bytes, bytes] | None:
    """(tiles, cells) of a terminated string, or None when the game must draw it."""
    body = value[: value.index(END)]
    if any(code >= 0xC0 and code != NEWLINE for code in body):
        return None
    tiles: dict[bytes, int] = {}
    cells = bytearray()
    for n, codes in enumerate(body.split(bytes([NEWLINE]))):
        if n:
            cells.append(CELL_NEWLINE)
        pixels = line(codes, anchored, stops)
        row = []
        for cell in range(len(codes)):
            tile = pixels[:, 8 * cell : 8 * cell + 8]
            row.append(tiles.setdefault(planar(tile), len(tiles) + 1) if tile.any() else 0)
        cells.extend(_trimmed(row, len(codes) - len(codes.rstrip(bytes([SPACE])))))
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
        ids = list(zip(id_list(rom, db.name), encoded, strict=True))
        columns = {value for sid, value in ids if sid in COLUMNS}
        stops = {value: STOPS[sid] for sid, value in ids if sid in STOPS}
        for value, address in place(db, encoded).items():
            baked = bake(value, value in columns, stops.get(value, ()))
            if baked:
                out.append((address, *baked))
    return sorted(out)


def width(codes: bytes) -> int:
    """The line's pixels up to its last ink."""
    ink = np.flatnonzero(line(codes, False).any(axis=0))
    return int(ink[-1]) + 1 if ink.size else 0


def wrapped(codes: bytes, limit: int) -> bytes:
    """The line broken at its last space that keeps the first row within `limit` px (unchanged when it fits)."""
    if width(codes) <= limit:
        return codes
    spaces = [i for i, code in enumerate(codes) if code == SPACE]
    for i in reversed(spaces):
        if width(codes[:i]) <= limit:
            return codes[:i] + bytes([NEWLINE]) + codes[i + 1 :]
    return codes


def combo_records(rom: Rom, source: Path) -> dict[int, tuple[bytes, bytes]]:
    """Special move position (id - COMBO_FIRST) -> (tiles, cells) of its battle16 name; COMBO_EMPTY's menu16 string
    at position COMBO_COUNT."""
    table = Table(str(TABLE))
    encoded, _ = wide_values(rom, "battle16", table, source / "battle16.xml")
    names = {
        sid - COMBO_FIRST: value
        for sid, value in zip(id_list(rom, "battle16"), encoded, strict=True)
        if COMBO_FIRST <= sid < COMBO_FIRST + COMBO_COUNT
    }
    menu, _ = wide_values(rom, "menu16", table, source / "menu16.xml")
    names[COMBO_COUNT] = dict(zip(id_list(rom, "menu16"), menu, strict=True))[COMBO_EMPTY]
    out = {}
    for k, value in names.items():
        if value[:1] != bytes([END]):
            body = value[: value.index(END)]
            if (baked := bake(wrapped(body, COMBO_PX) + bytes([END]), False)) is not None:
                out[k] = baked
    return out


def lr_table(rom: Rom, source: Path) -> bytes:
    """Per names8 id from LR_FIRST: the combo position of its special move when its battle16 name fits LR_PX on one
    row and has a record, else NO_TALENT."""
    encoded, _ = wide_values(rom, "battle16", Table(str(TABLE)), source / "battle16.xml")
    fits = {
        sid - COMBO_FIRST
        for sid, value in zip(id_list(rom, "battle16"), encoded, strict=True)
        if COMBO_FIRST <= sid < COMBO_FIRST + COMBO_COUNT
        and value[:1] != bytes([END])
        and width(value[: value.index(END)]) <= LR_PX
    }
    out = bytearray([NO_TALENT] * LR_COUNT)
    for first, talents in LR_TALENTS.items():
        for k, sid in enumerate(talents):
            if sid - COMBO_FIRST in fits:
                out[first - LR_FIRST + k] = sid - COMBO_FIRST
    return bytes(out)


def _record(n: int, tiles: bytes, cells: bytes, streams: dict[bytes, str], asm: list[str], out: Path) -> None:
    stream = "0"
    if tiles:
        if tiles not in streams:
            streams[tiles] = f"vwf8_stream_{len(streams)}"
            (out / f"{streams[tiles]}.bin").write_bytes(sdd1.compress(tiles))
            asm.append(f'.alloc {streams[tiles]} in text16 {{\n    .incbin "{streams[tiles]}.bin"\n}}')
        stream = streams[tiles]
    data = ", ".join(f"0x{b:02X}" for b in cells)
    asm.append(f".alloc vwf8_record_{n} in text16 {{\n    .dl {stream}\n    .db {len(tiles) // 16}, {data}\n}}")


def build(source: Path = ROOT / "text" / "fr", out: Path = ROOT / "build" / "gen") -> int:
    """vwf8_N.bin per distinct tile run and vwf8.i (streams, records, keys, combos in text16)."""
    rom = Rom()
    baked = records(rom, source)
    combos = combo_records(rom, source)
    streams: dict[bytes, str] = {}
    asm = [
        f"VWF8_KEYS := {len(baked)}",
        f"VWF8_COMBO_FIRST := 0x{COMBO_FIRST:04X}",
        f"VWF8_COMBOS := {COMBO_COUNT}",
        f"VWF8_COMBO_EMPTY := 0x{COMBO_EMPTY:04X}",
        f"VWF8_RECORDS := {len(baked) + COMBO_COUNT + 1}",
    ]
    keys = []
    for n, (address, tiles, cells) in enumerate(baked):
        _record(n, tiles, cells, streams, asm, out)
        keys.append(
            f"    .dw 0x{address & 0xFFFF:04X}\n    .db 0x{address >> 16:02X}, 0\n    .dl vwf8_record_{n}\n    .db 0"
        )
    asm.append(".alloc vwf8_keys in text16 {\n" + "\n".join(keys) + "\n}")
    rows = []
    for k in range(COMBO_COUNT + 1):
        if k in combos:
            _record(len(baked) + k, *combos[k], streams, asm, out)
            rows.append(f"    .dl vwf8_record_{len(baked) + k}\n    .db 0")
        else:
            rows.append("    .dl 0\n    .db 0")
    asm.append(".alloc vwf8_combos in text16 {\n" + "\n".join(rows) + "\n}")
    lr = lr_table(rom, source)
    asm += [
        f"VWF8_LR_FIRST := 0x{LR_FIRST:04X}",
        f"VWF8_LR_COUNT := {LR_COUNT}",
        f"VWF8_NO_TALENT := 0x{NO_TALENT:02X}",
    ]
    asm.append(".alloc vwf8_lr in text16 {\n    .db " + ", ".join(f"0x{b:02X}" for b in lr) + "\n}")
    for old in out.glob("names8_vwf*"):
        old.unlink()
    (out / "vwf8.i").write_text("\n".join(asm) + "\n")
    return len(baked) + len(combos)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} records")


if __name__ == "__main__":
    main()
