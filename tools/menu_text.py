"""Non-dialog text: four id-indexed string databases.

Every lookup (C2:3FF4, CA:B24C, CA:B278, CA:B2B0) linearly scans a u16 id list (0-terminated) and takes the
u16 at the same index of an offset list, relative to a string base. Several ids share one string.

* 8x8 strings (text/so_menu.tbl, CA:BCAD): bytes, C0-F2 voiced kana drawn with a dakuten tile on the row
  above, FC newline, FF end.
* 16x16 strings (C6:F6F9): u16 codes, glyph = code - 0x10 (dialog glyphs), 000D newline, FFFF end. Their
  table is derived from text/so_dialog.tbl into build/gen/so_menu16.tbl.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from katsuji.script import Table

from tools import sdd1
from tools.dialog import glyphs
from tools.lz import decode
from tools.rom import ROOT, Rom

SMALL_TABLE = ROOT / "text" / "so_menu.tbl"
WIDE_TABLE = ROOT / "build" / "gen" / "so_menu16.tbl"
WIDE_GLYPH_BASE = 0x10
INDEX_MAX = 0x1000  # bytes read for an id / offset list; the id list is 0-terminated well before

Loader = Callable[[Rom], tuple[bytes, bytes, bytes]]


@dataclass(frozen=True)
class Strings:
    name: str
    wide: bool
    load: Loader
    note: str

    @property
    def end(self) -> bytes:
        return b"\xff\xff" if self.wide else b"\xff"


@dataclass(frozen=True)
class Entry:
    ids: tuple[int, ...]  # every id pointing here, in id-list order
    offset: int
    value: bytes  # terminator included


def _rom_db(ids: int, offsets: int, base: int, end: int) -> Loader:
    def load(rom: Rom) -> tuple[bytes, bytes, bytes]:
        return rom.read(ids, INDEX_MAX), rom.read(offsets, INDEX_MAX), rom.read(base, end - base)

    return load


def _menu16(rom: Rom) -> tuple[bytes, bytes, bytes]:
    # CA:6328: S-DD1 ids -> $7F:2000, S-DD1 offsets -> $7F:2800, LZ strings -> $7F:3000.
    ids = sdd1.decompress(0xFE612F, 0x76C)[0]
    offsets = sdd1.decompress(0xFE5CF0, 0x76C)[0]
    return ids, offsets, decode(rom.read, 0xFE63A1)[0]


DATABASES = (
    Strings("names8", False, _rom_db(0xD706FA, 0xD70000, 0xD70DF6, 0xD80000), "D7: names (party, items, skills)"),
    Strings("labels8", False, _rom_db(0xFEA5CE, 0xFEA2E0, 0xFEA8BE, 0xFF0000), "FE: menu labels, ids EA60+"),
    Strings("battle16", True, _rom_db(0xD72A8D, 0xD7254B, 0xD72FD1, 0xD80000), "D7: battle / system messages"),
    Strings("menu16", True, _menu16, "FE:63A1 LZ: menu help and descriptions, ids EA60+"),
)


def _u16(data: bytes, o: int) -> int:
    return data[o] | data[o + 1] << 8


def _string_at(text: bytes, offset: int, end: bytes) -> bytes:
    p = offset
    while text[p : p + len(end)] != end:
        p += len(end)
    return text[offset : p + len(end)]


def entries(rom: Rom, db: Strings) -> list[Entry]:
    """One entry per distinct string offset, in id-list order of first use."""
    ids, offsets, text = db.load(rom)
    by_offset: dict[int, list[int]] = {}
    for i in range(0, len(ids) - 1, 2):
        sid = _u16(ids, i)
        if sid == 0:
            break
        by_offset.setdefault(_u16(offsets, i), []).append(sid)
    return [Entry(tuple(sids), off, _string_at(text, off, db.end)) for off, sids in by_offset.items()]


def write_wide_table() -> None:
    """16x16 menu table: u16 little-endian glyph + 0x10, derived from the dialog glyphs."""
    lines = [f"{(g + WIDE_GLYPH_BASE).to_bytes(2, 'little').hex().upper()}={t}" for g, t in glyphs().items()]
    lines += ["0D00=\\n", "FFFF=[end]"]
    WIDE_TABLE.parent.mkdir(parents=True, exist_ok=True)
    WIDE_TABLE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_for(db: Strings) -> Table:
    if not db.wide:
        return Table(str(SMALL_TABLE))
    write_wide_table()
    return Table(str(WIDE_TABLE))
