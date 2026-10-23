from __future__ import annotations

from pathlib import Path

from tools.item_list import ITEM_NAMES, ITEMS, build, widths
from tools.reflow import DialogLayout


def test_widths_measure_each_item_name() -> None:
    layout = DialogLayout({})
    table = widths(layout, {ITEM_NAMES + 0xB7: "Collier"})
    assert (len(table), table[0xB7]) == (ITEMS, layout.measure("Collier"))


def test_missing_item_measures_nothing() -> None:
    assert widths(DialogLayout({}), {})[0x10] == 0


def test_build_writes_the_table_and_constants(tmp_path: Path) -> None:
    table = build(tmp_path)
    assert (tmp_path / "item_widths.bin").read_bytes() == table
    assert "ITEM_LIST_WINDOW := 194" in (tmp_path / "item_list.i").read_text()
