"""Command ring labels: the French words fit their frames, and each record the patch repoints holds a label cel."""

from __future__ import annotations

import pytest

from tools import obj_letters, ring_labels, sdd1
from tools.rom import DEFAULT_ROM, Rom


@pytest.mark.parametrize("label", ring_labels.LABELS, ids=lambda label: label.text)
def test_a_label_fits_its_frame(label: ring_labels.Label) -> None:
    assert len(ring_labels.tiles(label)) == label.cels


def test_each_cel_has_its_slot() -> None:
    assert len(ring_labels.blob()) == sum(label.cels for label in ring_labels.LABELS) * ring_labels.SLOT


def test_a_slot_unpacks_to_its_cel() -> None:
    label = ring_labels.LABELS[0]
    slot = ring_labels.blob()[: ring_labels.SLOT]
    assert sdd1.decompress_bytes(slot, ring_labels.CEL)[0][: ring_labels.CEL] == ring_labels.tiles(label)[0]


def test_an_accent_takes_the_row_above_the_capitals() -> None:
    grid = obj_letters.paint("É", ring_labels.GLYPHS, 8, ring_labels.INK, ring_labels.INK)
    assert grid[0][3] == ring_labels.INK


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
@pytest.mark.parametrize("label", ring_labels.LABELS, ids=lambda label: label.text)
def test_the_frame_holds_8x8_cels_at_the_records_the_patch_repoints(label: ring_labels.Label) -> None:
    rom = Rom()
    header = rom.read(label.frame, 3)
    assert (header[0], header[1], header[2]) == (label.cels, label.cels * 2 - 1, 1)
    for cel in range(label.cels):
        record = rom.read(label.frame + 3 + cel * ring_labels.RECORD, ring_labels.RECORD)
        source = int.from_bytes(rom.read(label.source(cel), 3), "little")
        assert record[0] == 0
        assert int.from_bytes(record[1:3], "little") == cel * 8
        assert source >> 16 == 0xDC
