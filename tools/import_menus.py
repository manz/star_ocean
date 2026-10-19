"""Import the old French project's menu strings into text/fr/<db>.xml, one `<sn:string id="0xNNNN">` per string id.

* labels8: `Patch PRE ALPHA/TXT/menu.txt` (CP1252, `[PTn-OFFSET]` sections, OFFSET - 0x3EA2E0 = 2 * the position in
  the FE:A5CE id list). `SO-Magno/SO_items_fra.txt` has this block too, but in English.
* names8, battle16, menu16: `SO-Magno/SO_items_fra.txt` (UTF-8), blocks `$00` / `$01` / `$03`, `[ini $ID]` then
  the text up to `[end]` (sometimes misspelt), `[nl]` before each newline.

Their equipment slot icons (`<Arme>`...) were never drawn: the codes point at blank tiles, so they become words.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from tools.menu_text import DATABASES, _u16
from tools.rom import ROOT, Rom

LABELS_BASE = 0x3EA2E0  # FE:A2E0, their dumper's file offset of the offsets list
BLOCKS = {"names8": "00", "battle16": "01", "menu16": "03"}
SLOT_WORDS = {
    "<Arme>": "Arme",
    "<Armure>": "Armure",
    "<Bouclier>": "Bouclier",
    "<Casque>": "Casque",
    "<Bottes>": "Bottes",
    "<Accessoire>": "Accessoire",
}
GLYPHS = {"<Note>": "♪", "[NOTE]": "♪"}
ENTRY = re.compile(r"^\[ini \$([0-9A-Fa-f]+)\]\n", re.MULTILINE)
END = re.compile(r"\[e(?:n(?:d+)?)?(?:\]|$).*", re.DOTALL)  # "[end]", "[endd]", "[end]]", "[en" + what follows


def _glyphs(text: str) -> str:
    for tag, glyph in {**SLOT_WORDS, **GLYPHS}.items():
        text = text.replace(tag, glyph)
    return re.sub(r"<\$([0-9A-Fa-f]{2})>", lambda m: f"[0x{int(m[1], 16):x}]", text)


def labels(path: Path, ids: list[int]) -> dict[int, str]:
    raw = path.read_bytes().decode("cp1252").replace("\r", "")
    parts = re.split(r"^\[PT\d+-([0-9A-F]+)\]\n", raw, flags=re.MULTILINE)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("<End>", 1)[0].removesuffix("\n")
        out[ids[(int(parts[i], 16) - LABELS_BASE) // 2]] = _glyphs(body)
    return out


def magno_block(path: Path, block: str) -> dict[int, str]:
    text = path.read_text(encoding="utf-8")
    body = re.split(rf"^\[block \${block} [^\n]*\n", text, flags=re.MULTILINE)[1]
    body = re.split(r"^\[block ", body, flags=re.MULTILINE)[0]
    parts = ENTRY.split(body)
    out = {}
    for i in range(1, len(parts), 2):
        value = END.sub("", parts[i + 1].rstrip("\n"), count=1)
        out[int(parts[i], 16)] = _glyphs(value.replace("[nl]\n", "\n").replace("[nl]", "\n"))
    return out


def id_list(rom: Rom, name: str) -> list[int]:
    ids = next(db for db in DATABASES if db.name == name).load(rom)[0]
    out = []
    for i in range(0, len(ids) - 1, 2):
        if not _u16(ids, i):
            break
        out.append(_u16(ids, i))
    return out


def write_xml(strings: dict[int, str], path: Path) -> None:
    with path.open("w", encoding="utf-8") as fd:
        fd.write('<?xml version="1.0" encoding="utf-8"?>\n<sn:strings xmlns:sn="http://snes.ninja/ScriptNS">\n')
        for sid, text in sorted(strings.items()):
            fd.write(f"<sn:string id={quoteattr(f'0x{sid:04X}')}>{escape(text)}</sn:string>\n")
        fd.write("</sn:strings>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=Path, help='the old project\'s "SO SNES" folder')
    args = ap.parse_args()
    out = ROOT / "text" / "fr"
    rom = Rom()
    write_xml(
        labels(args.archive / "Patch PRE ALPHA" / "TXT" / "menu.txt", id_list(rom, "labels8")), out / "labels8.xml"
    )
    for name, block in BLOCKS.items():
        write_xml(magno_block(args.archive / "SO-Magno" / "SO_items_fra.txt", block), out / f"{name}.xml")
    print(f"labels8 + {', '.join(BLOCKS)} -> {out}")


if __name__ == "__main__":
    main()
