"""Item / talent notices: the C6:F523 templates (src/menu/text16.s) read in French order."""

from __future__ import annotations

import pytest

from tests.screens import IPS
from tools.encode_menus import french
from tools.rom import DEFAULT_ROM, ROOT, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists() or not IPS.exists(), reason="base ROM or build not present")

TABLE = 0xC6F523
FIELDS = {0x82: "<name>", 0x97: "<talent>", 0x17: "<level>"}
NAMES = {0x1387: "<item>", 0xF9C4: "<don>"}


def notice(number: int) -> str:
    rom = Rom().with_ips(IPS)
    strings = french(ROOT / "text" / "fr" / "menu16.xml")
    address = TABLE + int.from_bytes(rom.read(TABLE + 2 * number, 2), "little")
    out = ""
    while (kind := rom.read(address, 1)[0]) != 0x01:
        word = int.from_bytes(rom.read(address + 1, 2), "little")
        if kind == 0x07:
            out += strings[word]
        elif kind == 0x03:
            out += "\n"
        elif kind & 0x0F == 0x06:
            out += NAMES[word]
        else:
            out += FIELDS[kind]
        address += 3
    return out


@pytest.mark.parametrize(
    ("number", "text"),
    [
        (1, "Obtenu : <item> !"),
        (8, '<name> apprend le talent "<talent>" !'),
        (9, 'Le talent "<talent>" de <name>\npasse au niveau <level> !'),
        (10, "Création réussie : <item> !"),
        (11, "Identifié : <item> !"),
        (12, '<name> éveille un don inné secret :\n"<don>" !'),
    ],
)
def test_notice_reads_in_french_order(number: int, text: str) -> None:
    assert notice(number) == text
