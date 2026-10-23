"""Dump the Japanese script as snes.ninja ScriptNS XML: text/jp/scene_NN.xml and text/jp/<database>.xml.

Dialog pointer ids are message indexes in the scene block; database pointer ids are the game's string id
(the first one, when several ids share a string).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from katsuji.script.pointers import Pointer, write_pointers_as_xml

from tools.dialog import SCENES, dialog_table, messages, scene_block
from tools.menu_text import DATABASES, entries, table_for
from tools.rom import ROOT, Rom

OUT = ROOT / "text" / "jp"


def _pointer(pid: int, value: bytes) -> Pointer:
    pointer = Pointer(pid)
    pointer.value = value
    return pointer


def scene_path(out: Path, scene: int) -> Path:
    return out / f"scene_{scene:02d}.xml"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rom, table = Rom(), dialog_table()
    total = 0
    for scene in range(1, SCENES + 1):
        msgs = messages(scene_block(rom, scene))
        write_pointers_as_xml([_pointer(i, m) for i, m in enumerate(msgs)], table, str(scene_path(args.out, scene)))
        total += len(msgs)
    print(f"{total} messages in {SCENES} scenes -> {args.out}")
    for db in DATABASES:
        rows = entries(rom, db)
        pointers = [_pointer(e.ids[0], e.value) for e in rows]
        write_pointers_as_xml(pointers, table_for(db), str(args.out / f"{db.name}.xml"))
        print(f"{len(rows)} {db.name} strings -> {args.out}")


if __name__ == "__main__":
    main()
