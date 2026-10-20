"""Narration screens: the French lines render, fit, and the letter keeps its parchment."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import narration, sdd1
from tools.dump_images import NARRATION_LINE_BYTES
from tools.rom import DEFAULT_ROM, Rom

pytestmark = [
    pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present"),
    pytest.mark.skipif(not narration.FONT.exists(), reason="narration font not present"),
]


def test_every_drawn_line_is_a_stream(tmp_path: Path) -> None:
    lines = narration.build(out=tmp_path)
    streams = sorted(tmp_path.glob("narration_*.bin"))
    sizes = {sdd1.decompress_bytes(s.read_bytes(), NARRATION_LINE_BYTES)[1] == s.stat().st_size for s in streams}
    assert (lines, len(streams), sizes) == (19, 19, {True})


def test_letter_ink_is_erased_but_its_torn_edge_kept() -> None:
    grid = narration.erase_ink(narration.original(Rom(), 0))
    ink = [(x, y) for y, row in enumerate(grid) for x, v in enumerate(row) if v == narration.INK]
    assert ink and all(0 in narration.around(grid, x, y, 1) for x, y in ink)


def test_too_wide_line_is_refused() -> None:
    with pytest.raises(ValueError, match="px fit"):
        narration.coverage({"text": ["W" * 40]}, narration.MARGIN)
