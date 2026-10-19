"""Offline tooling against the base ROM; expected values were checked against live calls in kintsuki."""

from __future__ import annotations

import pytest

from tools.lz import decode
from tools.rom import DEFAULT_ROM, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


@pytest.fixture(scope="module")
def rom() -> Rom:
    return Rom()


@pytest.mark.parametrize(
    ("bus", "offset"),
    [(0x008000, 0x000000), (0xC263A0, 0x0263A0), (0xFF0000, 0x3F0000), (0xE841FC, 0x2841FC)],
)
def test_bus_offsets_follow_the_sdd1_board(rom: Rom, bus: int, offset: int) -> None:
    assert rom.offset(bus) == offset


@pytest.mark.parametrize(
    ("header", "size"),
    [(0xE841FC, 0x61C), (0xFFC800, 0x8000), (0xE6B87D, 0xE8F), (0xFD10BC, 0x10E)],
)
def test_lz_container_sizes_match_live_unpacks(rom: Rom, header: int, size: int) -> None:
    assert len(decode(rom.read, header)[0]) == size
