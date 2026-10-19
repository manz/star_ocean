"""French 8x8 menu strings -> a816 includes that rewrite a database's strings in place.

A database keeps its id list and its offset list where the game has them (dozens of routines index those with a
fixed bank); only the strings move, packed by a816 into the old strings' space (plus free bytes of the same bank)
and the offset list rewritten: offset = string - base, as the readers add it. Identical strings are stored once.
A string id the French lacks keeps the Japanese bytes.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from script import Table

from tools.import_menus import id_list
from tools.menu_text import DATABASES, _string_at, _u16
from tools.rom import ROOT, Rom

TABLE = ROOT / "text" / "so_menu_fr.tbl"
END = b"\xff"


@dataclass(frozen=True)
class SmallDb:
    name: str
    offsets: int  # bus address of the offset list
    base: int  # bus address the offsets are relative to
    ranges: tuple[tuple[int, int], ...]  # where the strings may go (inclusive), all in the base's bank


LABELS8 = SmallDb("labels8", 0xFEA2E0, 0xFEA8BE, ((0xFEA8BF, 0xFEBBFF),))  # old strings, then 891 free bytes


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


def build(source: Path, out: Path) -> None:
    rom, table = Rom(), Table(str(TABLE))
    for db in (LABELS8,):
        (out / f"{db.name}.i").write_text(include(db, values(rom, db, table, source / f"{db.name}.xml")))
