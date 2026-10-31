"""Narration screens: the French lines render, fit, and the letter keeps its parchment."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from kappan import Font

from tests.screens import assert_matches_golden
from tests.warp import field, run_script, warp
from tools import narration, sdd1
from tools.dump_images import NARRATION_LINE_BYTES
from tools.rom import DEFAULT_ROM, Rom
from tools.scene_asm import op

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


def test_every_drawn_line_is_a_stream(tmp_path: Path) -> None:
    lines = narration.build(out=tmp_path)
    streams = sorted(tmp_path.glob("narration_*.bin"))
    sizes = {sdd1.decompress_bytes(s.read_bytes(), NARRATION_LINE_BYTES)[1] == s.stat().st_size for s in streams}
    assert (lines, len(streams), sizes) == (19, 19, {True})


def test_letter_ink_is_erased_but_its_torn_edge_kept() -> None:
    grid = narration.erase_ink(narration.original(Rom(), 0))
    ink = [(x, y) for y, row in enumerate(grid) for x, v in enumerate(row) if v == narration.INK]
    assert ink and all(0 in narration.around(grid, x, y, 1) for x, y in ink)


def test_letter_creases_clear_around_the_ink() -> None:
    parchment = narration.erase_ink(narration.original(Rom(), 0))
    grid = narration.letter(Rom(), {"text": ["Le chef du village de Laponia"]})
    french = [
        (x, y)
        for y, row in enumerate(grid)
        for x, v in enumerate(row)
        if v == narration.INK and parchment[y][x] != narration.INK
    ]
    assert french
    assert narration.CREASE not in {v for x, y in french for v in narration.around(grid, x, y, 1)}


def test_too_wide_line_is_refused() -> None:
    with pytest.raises(ValueError, match="px fit"):
        narration.coverage({"text": ["W" * 40]}, narration.MARGIN, Font(narration.FONT, narration.SIZE))


KURT = 4  # a scene 6 map (its start-up branches on map ids 4-13)
CHIEF_LETTER = 52  # scene 6's `say_mode8 52`: [narration][0x0], the chief's letter
LETTER_ROWS = np.s_[144:]  # the parchment; a candle flickers above it


def test_the_chief_letter_shows_in_kurt() -> None:
    emu = field("fantasyanime_4")
    warp(emu, KURT, 8, 8, 2)
    emu.run_frames(60)
    run_script(emu, [op("say_mode8", CHIEF_LETTER)], frames=120)
    assert_matches_golden(emu, "chief_letter", LETTER_ROWS)
