"""The battle spell list's names8 strings (0x07D0-0x07F9): the menus' menu16 names, within a column of the list."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from katsuji.script import Table

from tools.encode_menus import TABLE
from tools.rom import ROOT
from tools.vwf8 import width

FIRST, COUNT = 0x07D0, 0x2A  # names8 ids of the spells
MENU_FIRST = 0xFA00  # their menu16 entries: the name, then the description
COLUMN_PX = 8 * 8  # the list's columns start 9 cells apart: a cell kept between names


def _strings(name: str) -> dict[int, str]:
    root = ET.parse(ROOT / "text" / "fr" / f"{name}.xml").getroot()
    return {int(e.get("id", "0"), 16): e.text or "" for e in root}


def test_battle_spell_names_are_the_menus_names() -> None:
    names, menu = _strings("names8"), _strings("menu16")
    assert [names[FIRST + k] for k in range(COUNT)] == [menu[MENU_FIRST + k].split("\n")[0] for k in range(COUNT)]


def test_every_spell_name_fits_its_column() -> None:
    table, names = Table(str(TABLE)), _strings("names8")
    assert [hex(FIRST + k) for k in range(COUNT) if width(table.to_bytes(names[FIRST + k])) > COLUMN_PX] == []
