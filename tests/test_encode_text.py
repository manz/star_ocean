"""French scene blocks: the LZSS container round-trips through the game's decoder, every scene fits SRAM."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from tools.dialog import build_block, messages, scene_block
from tools.encode_text import SRAM_TEXT, container, fr_table, scene_values
from tools.lz import decode
from tools.rom import DEFAULT_ROM, ROOT, Rom

SCENES = sorted((ROOT / "text" / "fr").glob("scene_*.xml"))


def _unpack(data: bytes) -> bytes:
    return decode(lambda address, size: data[address : address + size], 0)[0]


@pytest.mark.parametrize(
    "data",
    [b"", b"a", b"abc" * 100, bytes(range(256)) * 20, random.Random(1).randbytes(5000), b"\x00" * 4000],
    ids=["empty", "one", "repeat", "ramp", "random", "zeros"],
)
def test_container_round_trips(data: bytes) -> None:
    assert _unpack(container(data)) == data


def test_container_header_carries_sizes() -> None:
    packed = container(b"hello hello hello")
    assert (packed[0], int.from_bytes(packed[1:3], "little"), int.from_bytes(packed[5:7], "little")) == (
        0x81,
        len(packed) - 9,
        17,
    )


def test_letters_take_one_byte() -> None:
    assert fr_table().to_bytes("Qu'est-ce ?") == bytes.fromhex("203e612e3c3d652c2e0560")


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
@pytest.mark.parametrize("path", SCENES, ids=lambda p: p.stem)
def test_scene_fits_sram_and_keeps_message_count(path: Path) -> None:
    japanese = messages(scene_block(Rom(), int(path.stem.split("_")[1])))
    values, _ = scene_values(path, fr_table(), japanese)
    assert len(values) == len(japanese) and len(build_block(values)) <= SRAM_TEXT
