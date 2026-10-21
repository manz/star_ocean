"""Yes / no bubbles: "Oui" / "Non" fit inside the Japanese bubbles, keep their rim and compress back."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import sdd1, yes_no
from tools.cutscene_text import tile
from tools.rom import DEFAULT_ROM, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")

RIM = {0, 1}


@pytest.mark.parametrize("bubble", yes_no.BUBBLES, ids=lambda b: b.name)
def test_the_rim_is_kept(bubble: yes_no.Bubble) -> None:
    old = yes_no.original(Rom(), bubble.frame)
    new = yes_no.french(old, bubble)
    assert [[v if v in RIM else None for v in row] for row in new] == [
        [v if v in RIM else None for v in row] for row in old
    ]


@pytest.mark.parametrize("bubble", yes_no.BUBBLES, ids=lambda b: b.name)
def test_the_word_and_its_shade_sit_on_the_ground(bubble: yes_no.Bubble) -> None:
    old = yes_no.blank(yes_no.original(Rom(), bubble.frame), bubble.style)
    new = yes_no.french(yes_no.original(Rom(), bubble.frame), bubble)
    changed = {old[y][x] for y, row in enumerate(new) for x, v in enumerate(row) if v != old[y][x]}
    assert changed == {yes_no.GROUND}


@pytest.mark.parametrize("bubble", yes_no.BUBBLES, ids=lambda b: b.name)
def test_no_japanese_ink_is_left(bubble: yes_no.Bubble) -> None:
    grid = yes_no.blank(yes_no.original(Rom(), bubble.frame), bubble.style)
    assert all(v != yes_no.INK for row in grid for v in row)


def test_each_cel_decompresses_to_the_french_bubble(tmp_path: Path) -> None:
    grids = yes_no.build(out=tmp_path)
    rom = Rom()
    for bubble in yes_no.BUBBLES:
        grid = grids[bubble.name]
        for n, cel in enumerate(yes_no.cels(rom, bubble.frame)):
            blob = (tmp_path / f"yes_no_{bubble.name}_{n}.bin").read_bytes()
            if cel.size:
                top, size = sdd1.decompress_bytes(blob, 0x40)
                bottom, _ = sdd1.decompress_bytes(blob[size:], 0x40)
                expected = b"".join(tile(grid, cel.dx + dx, cel.dy + dy) for dy, dx in ((0, 0), (0, 8), (8, 0), (8, 8)))
                assert top + bottom == expected
            else:
                assert sdd1.decompress_bytes(blob, 0x20)[0] == tile(grid, cel.dx, cel.dy)
