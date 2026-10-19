"""S-DD1 codec: game streams decode, the compressor round-trips."""

from __future__ import annotations

import random

import pytest

from tools import sdd1
from tools.rom import DEFAULT_ROM, Rom

# (stream, size, compressed size), checked once against the chip's decoder
STREAMS = [(0xDBA078, 0xC00, 1954), (0xFE612F, 0x76C, 616), (0xFE5CF0, 0x76C, 1075), (0xFE3CAD, 0x1000, 2144)]


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
@pytest.mark.parametrize(("address", "size", "packed"), STREAMS, ids=lambda v: f"{v:X}")
def test_game_stream_round_trips(address: int, size: int, packed: int) -> None:
    data, read = sdd1.decompress(address, size, Rom())
    again = sdd1.compress(data)
    assert (read, sdd1.decompress_bytes(again, size)[0], len(again) <= packed) == (packed, data, True)


@pytest.mark.parametrize(
    "data",
    [b"\0", b"\xff" * 33, bytes(range(256)) * 4, random.Random(7).randbytes(777), b"\x55\xaa" * 300],
    ids=["zero", "ones-odd", "ramp", "random", "pattern"],
)
def test_round_trips(data: bytes) -> None:
    assert sdd1.decompress_bytes(sdd1.compress(data), len(data))[0] == data


@pytest.mark.parametrize("header", sdd1.HEADERS, ids=lambda h: f"{h:02X}")
def test_every_header_round_trips(header: int) -> None:
    data = random.Random(header).randbytes(300)
    packed = sdd1._encode(data, header)
    assert (packed[0] & 0xF0, sdd1.decompress_bytes(packed, len(data))[0]) == (header, data)
