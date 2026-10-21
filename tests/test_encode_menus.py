"""Menu string placement: the reclaimed Japanese scene text never reaches a neighbouring container."""

from __future__ import annotations

import pytest

from tools.dialog import SCENE_TABLE, SCENES
from tools.encode_menus import free_scene_text
from tools.rom import DEFAULT_ROM, ROOT, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


def test_free_scene_text_spares_the_event_data() -> None:
    rom = Rom()
    events = [int.from_bytes(rom.read(SCENE_TABLE + scene * 6, 3), "little") for scene in range(SCENES)]
    ranges = free_scene_text(rom, ROOT / "text" / "fr")
    assert [hex(e) for e in events if any(lo <= e <= hi for lo, hi in ranges)] == []
