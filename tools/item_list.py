"""Item name widths for the item list message (src/dialog/chest.s): the list breaks its own lines between items.

The dialog engine breaks a line at whichever glyph passes the window, mid-word, and a second such break in one
message draws over the line before. The list builder measures instead: a byte per item id (names8 id
ITEM_NAMES + id), the name's width in the dialog font as the reflow measures it.
"""

from __future__ import annotations

from pathlib import Path

from tools.encode_menus import french
from tools.reflow import WINDOW_WIDTH, DialogLayout
from tools.rom import ROOT

ITEM_NAMES = 0x1387  # names8 id of item 0 (C6:DAD7 adds it to the id)
ITEMS = 0x200  # ids are 9 bits: the slot word's low byte, bit 15 the ninth
SEPARATOR = ", "
SOURCE = ROOT / "text" / "fr" / "names8.xml"


def widths(layout: DialogLayout, names: dict[int, str]) -> bytes:
    """Each item's name width in pixels, 0 for an id names8 lacks."""
    return bytes(layout.measure(names.get(ITEM_NAMES + item, "")) for item in range(ITEMS))


def build(out: Path = ROOT / "build" / "gen", source: Path = SOURCE) -> bytes:
    """item_widths.bin, and item_list.i: the separator's and the comma's widths, the window's."""
    layout = DialogLayout({})
    table = widths(layout, french(source))
    out.mkdir(parents=True, exist_ok=True)
    (out / "item_widths.bin").write_bytes(table)
    (out / "item_list.i").write_text(
        f"ITEM_LIST_WINDOW := {WINDOW_WIDTH}\n"
        f"ITEM_LIST_SEPARATOR := {layout.measure(SEPARATOR)}\n"
        f"ITEM_LIST_COMMA := {layout.measure(SEPARATOR[0])}\n"
    )
    return table
