"""French menu strings -> a816 includes.

8x8 databases (labels8, names8) keep their id list and offset list where the game has them (dozens of routines
index those with a fixed bank); only the strings move, packed by a816 into the old strings' space (plus free bytes
of the same bank) and the offset list rewritten: offset = string - base, as the readers add it. A string id the
French lacks keeps the Japanese bytes.

16x16 databases (battle16, menu16) were u16 per character, too big in French: their strings become one byte per
character (glyph + 0x10, build/gen/so_menu16_fr.tbl), anywhere in the text16 pool, found through a 24-bit pointer per
id-list position (src/menu/text16.s widens them back where the game wants u16). A string id the French lacks is
empty. Identical strings are stored once.

`C0:4B60` turns an 8x8 code into a 16x16 / dialog glyph: rebuilt from the two French tables.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from script import Table

from tools import menu_font16
from tools.dialog import SCENES, scene_text_ptr
from tools.import_menus import id_list
from tools.lz import decode
from tools.menu_text import DATABASES, _string_at, _u16
from tools.rom import ROOT, Rom

TABLE = ROOT / "text" / "so_menu_fr.tbl"
TABLE16 = menu_font16.TABLE
END = b"\xff"
GLYPH_MAP, GLYPH_MAP_SIZE = 0xC04B60, 0xF3  # up to the LZ container at C0:4C53
TEXT16_FF = (0xFF1800, 0xFFBF7F)  # after the 16x16 font (room for 192 glyphs), up to the end of the kanji
SAME = {"\u201c": '"', "\u201d": '"'}


@dataclass(frozen=True)
class SmallDb:
    name: str
    offsets: int  # bus address of the offset list
    base: int  # bus address the offsets are relative to
    ranges: tuple[tuple[int, int], ...]  # where the strings may go (inclusive), all in the base's bank


LABELS8 = SmallDb("labels8", 0xFEA2E0, 0xFEA8BE, ((0xFEA8BF, 0xFEBBFF),))  # old strings, then 891 free bytes
# Its old strings, battle16's (moved out) and the free bytes after them.
NAMES8 = SmallDb("names8", 0xD70000, 0xD70DF6, ((0xD70DF6, 0xD7254A), (0xD72FD1, 0xD743FF)))
WIDE = ("battle16", "menu16")


def french(path: Path) -> dict[int, str]:
    return {int(e.get("id", "0"), 16): e.text or "" for e in ET.parse(path).getroot()}


def japanese(rom: Rom, name: str) -> list[bytes]:
    """The game's strings by id-list position."""
    _, offsets, text = next(db for db in DATABASES if db.name == name).load(rom)
    count = len(id_list(rom, name))
    return [_string_at(text, _u16(offsets, 2 * i), END) for i in range(count)]


def values(rom: Rom, db: SmallDb, table: Table, source: Path) -> list[bytes]:
    """Each id-list position's bytes, terminator included."""
    strings = french(source)
    return [
        table.to_bytes(strings[sid]) + END if sid in strings else jp
        for sid, jp in zip(id_list(rom, db.name), japanese(rom, db.name), strict=True)
    ]


def _normalise(text: str) -> str:
    for a, b in SAME.items():
        text = text.replace(a, b)
    return text


def include(db: SmallDb, encoded: list[bytes]) -> str:
    pool = f"{db.name}_text"
    lines = [f".pool {pool} {{"]
    lines += [f"    range 0x{lo:06X} 0x{hi:06X}" for lo, hi in db.ranges]
    lines += ["    strategy pack", "}"]
    labels: dict[bytes, str] = {}
    for value in encoded:
        if value not in labels:
            labels[value] = f"{db.name}_{len(labels)}"
            data = ", ".join(f"0x{b:02X}" for b in value)
            lines += [f".alloc {labels[value]} in {pool} {{", f"    .db {data}", "}"]
    lines += [f".alloc {db.name}_offsets at 0x{db.offsets:06X} size {2 * len(encoded)} {{"]
    lines += [f"    .dw ({labels[value]} - 0x{db.base:06X}) & 0xFFFF" for value in encoded]
    lines += ["}"]
    return "\n".join(lines) + "\n"


def wide_values(rom: Rom, name: str, table: Table, source: Path) -> tuple[list[bytes], int]:
    """Each id-list position's bytes, terminator included, and how many ids the French lacks."""
    strings = french(source)
    ids = id_list(rom, name)
    out = [table.to_bytes(_normalise(strings[sid])) + END if sid in strings else END for sid in ids]
    return out, sum(sid not in strings for sid in ids)


def free_scene_text(rom: Rom, source: Path) -> list[tuple[int, int]]:
    """The Japanese scene text blocks of the scenes the patch repoints (tools/encode_text.py), split at banks."""
    spans = set()
    for scene in range(1, SCENES + 1):
        if (source / f"scene_{scene:02d}.xml").exists():
            start = scene_text_ptr(rom, scene)
            spans.add((start, start + decode(rom.read, start)[1] - 1))
    merged: list[tuple[int, int]] = []
    for lo, hi in sorted(spans):
        if merged and lo <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
        else:
            merged.append((lo, hi))
    out = []
    for lo, hi in merged:
        while lo >> 16 != hi >> 16:
            out.append((lo, lo | 0xFFFF))
            lo = (lo | 0xFFFF) + 1
        out.append((lo, hi))
    return out


def wide_include(databases: dict[str, list[bytes]], ranges: list[tuple[int, int]]) -> str:
    lines = [".pool text16 {"]
    lines += [f"    range 0x{lo:06X} 0x{hi:06X}" for lo, hi in ranges]
    lines += ["    strategy pack", "}"]
    labels: dict[bytes, str] = {}
    for encoded in databases.values():
        for value in encoded:
            if value not in labels:
                labels[value] = f"text16_{len(labels)}"
                data = ", ".join(f"0x{b:02X}" for b in value)
                lines += [f".alloc {labels[value]} in text16 {{", f"    .db {data}", "}"]
    for name, encoded in databases.items():
        lines += [f".alloc {name}_pointers in text16 {{"]
        lines += [f"    .dl {labels[value]}" for value in encoded]
        lines += ["}"]
    return "\n".join(lines) + "\n"


def glyph_map(table: Table, table16: Table) -> bytes:
    """C0:4B60: 8x8 code -> 16x16 glyph (code - 0x10), 0 (space) for a code without one."""
    out = bytearray(GLYPH_MAP_SIZE)
    for code in range(GLYPH_MAP_SIZE):
        char = table.inverted_lookup.get(bytes([code]))
        wide = table16.lookup.get(char) if isinstance(char, str) else None
        if wide is not None and wide[0] >= menu_font16.BASE:
            out[code] = wide[0] - menu_font16.BASE
    return bytes(out)


def glyph_map_include(data: bytes) -> str:
    rows = [", ".join(f"0x{b:02X}" for b in data[i : i + 16]) for i in range(0, len(data), 16)]
    body = "\n".join(f"    .db {row}" for row in rows)
    return f".alloc glyph_map at 0x{GLYPH_MAP:06X} size {len(data)} {{\n{body}\n}}\n"


def build(source: Path, out: Path) -> list[str]:
    rom, table, table16 = Rom(), Table(str(TABLE)), Table(str(TABLE16))
    for db in (LABELS8, NAMES8):
        (out / f"{db.name}.i").write_text(include(db, values(rom, db, table, source / f"{db.name}.xml")))
    report, databases = [], {}
    for name in WIDE:
        databases[name], missing = wide_values(rom, name, table16, source / f"{name}.xml")
        if missing:
            report.append(f"{name}: {missing} ids without French, left empty")
    ranges = [TEXT16_FF, *free_scene_text(rom, source)]
    (out / "text16.i").write_text(wide_include(databases, ranges))
    (out / "glyph_map.i").write_text(glyph_map_include(glyph_map(table, table16)))
    return report
