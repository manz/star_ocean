"""The map records (FF:C800, notes/text/map_table.md): one LZ block of 0x30-byte records by map id, unpacked to
$7F:0000 on every map load. Byte 0x21 is the map's scene; 0 marks an unused id.
"""

from __future__ import annotations

from collections import defaultdict
from functools import cache

from tools.lz import decode
from tools.rom import Rom

MAP_TABLE = 0xFFC800
RECORD = 0x30
SCENE = 0x21


@cache
def records() -> tuple[bytes, ...]:
    """Every record, by map id, up to the last one in use."""
    data = decode(Rom().read, MAP_TABLE)[0]
    recs = [data[m * RECORD : (m + 1) * RECORD] for m in range(len(data) // RECORD)]
    while recs and not any(recs[-1]):
        recs.pop()
    return tuple(recs)


def map_scenes() -> dict[int, int]:
    """Map id → scene, for the maps that have one."""
    return {m: rec[SCENE] for m, rec in enumerate(records()) if rec[SCENE]}


def scene_maps() -> dict[int, frozenset[int]]:
    """Scene → its maps."""
    maps: dict[int, set[int]] = defaultdict(set)
    for m, scene in map_scenes().items():
        maps[scene].add(m)
    return {scene: frozenset(ms) for scene, ms in maps.items()}
