"""What a save slot holds, read from the game's own layout table (C2:D119, read by the loader C2:D53E): records of
(count, 24-bit WRAM address), the slot's bytes taken in order from slot + 0x25C. Three 0xA00-byte slots at the start of
the .srm (src/core/saves.s). Covers the story block (map, position, Fol, flags, story variables); party records and
items come from other loops.
"""

from __future__ import annotations

from functools import cache

from tools.rom import Rom

LAYOUT = 0xC2D119
SLOT_SIZE = 0xA00
SLOTS = 3
START = 0x25C  # the first record's bytes in the slot
MAP = 0x7E043D
STORY = 0x7EFED3  # var.w[0x10], the story counter
FLAGS = 0x7EFE73  # 32 bytes of scene flags (ops 31-33)


@cache
def layout() -> tuple[tuple[int, int, int], ...]:
    """(slot offset, size, WRAM address) for each record."""
    rom, at, offset, rows = Rom(), LAYOUT, START, []
    while size := rom.read(at, 1)[0]:
        address = int.from_bytes(rom.read(at + 1, 3), "little")
        rows.append((offset, size, address | 0x7E0000 if address < 0x10000 else address))
        offset, at = offset + size, at + 4
    return tuple(rows)


def slot(srm: bytes, n: int) -> bytes:
    return srm[n * SLOT_SIZE : (n + 1) * SLOT_SIZE]


def read(data: bytes, address: int, size: int) -> bytes:
    """`size` bytes the slot puts at WRAM `address`."""
    for offset, count, start in layout():
        if start <= address and address + size <= start + count:
            at = offset + address - start
            return data[at : at + size]
    raise KeyError(f"{address:06X} is not in the slot")


def used(data: bytes) -> bool:
    return any(data)


def story(data: bytes) -> int:
    return int.from_bytes(read(data, STORY, 2), "little")


def map_id(data: bytes) -> int:
    return int.from_bytes(read(data, MAP, 2), "little")
