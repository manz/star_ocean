"""Town badge: "ActionPrivée" fits the Japanese strip, keeps its frame and compresses back."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import badge, sdd1
from tools.cutscene_text import tile
from tools.rom import DEFAULT_ROM, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


def test_the_rounded_end_is_kept() -> None:
    old = badge.original(Rom())
    new = badge.french(old)
    assert [row[40:] for row in new[: badge.SPLIT]] == [row[40:] for row in old[: badge.SPLIT]]


def test_the_acute_sits_over_the_first_e() -> None:
    new = badge.french(badge.original(Rom()))
    assert (new[6][38], new[7][37]) == (badge.INK, badge.INK)


def test_each_cel_is_two_streams_back_to_back(tmp_path: Path) -> None:
    grid = badge.build(out=tmp_path)
    for cel in range(badge.CELS):
        blob = (tmp_path / f"badge_{cel}.bin").read_bytes()
        top, size = sdd1.decompress_bytes(blob, badge.CEL_BYTES)
        bottom, _ = sdd1.decompress_bytes(blob[size:], badge.CEL_BYTES)
        assert top + bottom == tile(grid, cel * 16, 0) + tile(grid, cel * 16 + 8, 0) + tile(grid, cel * 16, 8) + tile(
            grid, cel * 16 + 8, 8
        )
