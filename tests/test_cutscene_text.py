"""Cutscene text: French sprite frames and credit titles render, and land where the Japanese ones were."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import cutscene_text, sdd1
from tools.rom import DEFAULT_ROM, Rom

needs_rom = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
needs_fonts = pytest.mark.skipif(
    not all(style[0].exists() for style in cutscene_text.STYLES.values()), reason="cutscene fonts not present"
)


@needs_rom
@needs_fonts
def test_every_frame_and_title_is_written(tmp_path: Path) -> None:
    frames = cutscene_text.build(out=tmp_path)
    asm = (tmp_path / "cutscenes.i").read_text()
    assert (frames, asm.count("in cutscene_frames"), asm.count('"credit_title_')) == (18, 18, 5)


@needs_rom
def test_japanese_frame_centre_is_its_header() -> None:
    assert cutscene_text.old_centre(Rom(), 0xCC2F84) == (112, 8, 0x73)  # 14 cels, 224x16


@needs_rom
def test_japanese_title_edges() -> None:
    first, last = cutscene_text.title_edges(Rom(), 0xFD9D68)  # "Game Design", left-aligned
    assert first < 32 < last < 128


@needs_fonts
def test_title_stream_round_trips() -> None:
    grid = cutscene_text.render(["Avec"], "credit", width=256, right=220)
    stream = cutscene_text.title_stream(grid)
    assert sdd1.decompress_bytes(sdd1.compress(stream), cutscene_text.TITLE_BYTES)[0] == stream


def test_touching_ranges_merge() -> None:
    assert cutscene_text.spans([(5, 9), (0, 5), (12, 14)]) == [(0, 9), (12, 14)]
