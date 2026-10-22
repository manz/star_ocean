"""Party names in WRAM: a 12-byte record per character at $7E:1548, a name of up to 6 8x8 codes then 0xFF, a
nickname of up to 4 then 0xFF. The name entry edits them, saves keep them (6 + 4 codes) and the dialog inserts
read them through the slots at C2:3F21: [nick:] reads Ratix's nickname but every other character's name,
[name:] the other way round.

build/gen/party_names.i holds the new game records (French names8 ids 11-1C, nicknames 01-0C cut to 4 codes) and
the default names older saves hold, Japanese, DeJap's English or this patch's earlier spellings, that loading a
save replaces (src/dialog/names.s).
"""

from __future__ import annotations

from pathlib import Path

from script import Table

from tools.encode_menus import TABLE, french, japanese
from tools.import_legacy import NAMES as JP_NAMES
from tools.import_legacy import NICKNAMES
from tools.import_menus import id_list
from tools.rom import ROOT, Rom

NAME, NICKNAME, END = 6, 4, 0xFF
PARTY = 12
NAME_IDS, NICKNAME_IDS = range(0x11, 0x11 + PARTY), range(0x01, 0x01 + PARTY)
RATIX = 0  # the one character whose [nick:] reads the nickname
RECORD = NAME + NICKNAME + 2
DEJAP = ["Ratix", "Milly", "Dorn", "Ronixis", "Iria", "Cius", "Joshua", "Tinek", "Marvel", "Ashlay", "Perisie", "Fear"]
OLD_FRENCH = ["", "", "", "Ronixis", "", "", "", "", "", "", "Perisie", ""]  # this patch's names before they fit
SOURCE = ROOT / "text" / "fr" / "names8.xml"


def french_names(source: Path = SOURCE) -> tuple[list[str], list[str]]:
    """The names and the nicknames a new game starts with."""
    strings = french(source)
    return [strings[i] for i in NAME_IDS], [strings[i][:NICKNAME] for i in NICKNAME_IDS]


def record(name: bytes, nickname: bytes) -> bytes:
    if len(name) > NAME:
        raise ValueError(f"{name!r}: {len(name)} codes, the name slot holds {NAME}")
    return (
        name
        + bytes([END]) * (NAME + 1 - len(name))
        + nickname[:NICKNAME]
        + bytes([END]) * (NICKNAME + 1 - len(nickname[:NICKNAME]))
    )


def defaults(table: Table, source: Path = SOURCE) -> bytes:
    names, nicknames = french_names(source)
    return b"".join(record(table.to_bytes(n), table.to_bytes(k)) for n, k in zip(names, nicknames, strict=True))


def japanese_names(rom: Rom) -> list[bytes]:
    strings = dict(zip(id_list(rom, "names8"), japanese(rom, "names8"), strict=True))
    return [strings[i].split(bytes([END]))[0] for i in NAME_IDS]


def dejap_names() -> list[bytes]:
    """The names a save made with DeJap's English patch holds (tests/saves/fantasyanime_*.srm): capitals at
    ASCII - 0x20, small letters at ASCII - 0x1F, cut to the slot."""
    return [bytes(ord(c) - (0x1F if c.islower() else 0x20) for c in name)[:NAME] for name in DEJAP]


def older(rom: Rom, table: Table) -> bytes:
    """Fixup entries, 0xFF after the last: record, bytes of the French record to copy (the whole record when the
    nickname is unreadable, the name alone when it is French), the name it replaces ended by 0xFF and padded."""
    out = b""
    sets = [(japanese_names(rom), RECORD), (dejap_names(), RECORD)]
    sets.append(([table.to_bytes(name)[:NAME] for name in OLD_FRENCH], NAME + 1))
    for names, count in sets:
        for n, name in enumerate(names):
            if name:
                out += bytes([n, count]) + name + bytes([END]) * (NAME + 1 - len(name))
    return out + bytes([END])


def inserts(source: Path = SOURCE) -> dict[str, str]:
    """Dialog tag name -> the French a new game's insert prints, for the layout's measure."""
    names, nicknames = french_names(source)
    nick = [nicknames[RATIX], *names[RATIX + 1 :]]
    name = [names[RATIX], *nicknames[RATIX + 1 :]]
    return dict(zip(JP_NAMES, name, strict=True)) | dict(zip(NICKNAMES, nick, strict=True))  # [nick:] the common one


def _rows(label: str, data: bytes, width: int) -> str:
    rows = [", ".join(f"0x{b:02X}" for b in data[i : i + width]) for i in range(0, len(data), width)]
    return f".alloc {label} in code_c4 {{\n" + "\n".join(f"    .db {row}" for row in rows) + "\n}\n"


def build(out: Path, rom: Rom | None = None, source: Path = SOURCE) -> None:
    rom = rom or Rom()
    table = Table(str(TABLE))
    text = _rows("party_names_default", defaults(table, source), RECORD)
    text += _rows("party_names_older", older(rom, table), NAME + 3)
    (out / "party_names.i").write_text(text, encoding="utf-8")
