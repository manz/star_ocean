"""Scene event edits: each one finds the bytes it expects, keeps the length, and the packed block unpacks to them."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.lz import decode
from tools.rom import DEFAULT_ROM, Rom
from tools.scene_events import EDITS, Edit, build, edited, event_pointer

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="no base ROM")


def _unpack(data: bytes) -> bytes:
    return decode(lambda address, size: data[address : address + size], 0)[0]


@pytest.mark.parametrize("scene", sorted(EDITS))
def test_edits_change_only_their_bytes(scene: int) -> None:
    rom = Rom()
    before = decode(rom.read, event_pointer(rom, scene))[0]
    after = edited(rom, scene, EDITS[scene])
    changed = {i for i, (a, b) in enumerate(zip(before, after, strict=True)) if a != b}
    allowed = {e.offset + i for e in EDITS[scene] for i in range(len(e.new))}
    assert changed and changed <= allowed


def test_scene_80_door_skips_letter_two() -> None:
    """Set 4, letter 1 in slot 3, letter 3 in slot 2: GAÏA from "A I G A" with either A second."""
    door = edited(Rom(), 80, EDITS[80])[0x39B:0x3B3]
    assert door.hex(" ") == "00 80 4c 00 04 01 00 80 4d 00 03 01 00 80 4c 00 04 01 00 80 4f 00 02 ff"


def test_stale_bytes_are_refused() -> None:
    with pytest.raises(ValueError, match="expected"):
        edited(Rom(), 80, [Edit(0x3A7, b"\x01\x02\x03\x04\x05", b"\x00" * 5, "wrong")])


def test_build_packs_and_repoints(tmp_path: Path) -> None:
    build(tmp_path)
    assert _unpack((tmp_path / "scene_events" / "80.bin").read_bytes()) == edited(Rom(), 80, EDITS[80])
    assert ".alloc at 0xE401DA size 3 {" in (tmp_path / "scene_events.i").read_text()
