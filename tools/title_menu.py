"""Render the French title menu (text/fr/title_menu.toml) into the title sprite sheet for src/dialog/title_menu.s.

The title sheet is one 0x1C00-byte S-DD1 stream (DA:F458) DMAed to the sprite tiles 0x100-0x1DF by CC:2441. The
menu items are sprite frames (C3:8ECB) of VRAM cels: a header (0x80 | cel count, width and height bytes), then
7-byte cels: size (1 = 16x16), dx and dy (s16), tile. The Japanese items' cels are freed and the French ones drawn
in their place (17 cels: a 16x16 cel is tiles t, t + 1, t + 16, t + 17); the sheet is compressed again into text16
and the frames go in the bank CC cutscene_frames pool, their sprite-list words repointed.
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path
from typing import Any

from tools import sdd1
from tools.cutscene_text import CEL, preview, render, tile
from tools.rom import ROOT, Rom

SHEET, SHEET_BYTES, FIRST_TILE = 0xDAF458, 0x1C00, 0x100
SHEET_ADDRESS, SHEET_BANK = 0xCC2442, 0xCC2448  # the ldx #$F458 and lda #$DA operands at CC:2441
TILE_BYTES = 32
SLOTS = [0x18E, *range(0x1A0, 0x1B0, 2), *range(0x1C0, 0x1D0, 2)]  # the Japanese cels and the two free after them


def _put(sheet: bytearray, tile_number: int, data: bytes) -> None:
    at = (tile_number - FIRST_TILE) * TILE_BYTES
    sheet[at : at + TILE_BYTES] = data


def frame_at(rom: Rom, entry: int) -> int:
    return 0xCC0000 | int.from_bytes(rom.read(entry, 2), "little")


def build(src: Path = ROOT / "text" / "fr" / "title_menu.toml", out: Path = ROOT / "build" / "gen") -> int:
    """title_sheet.bin, previews in title_menu/, title_menu.i (sheet, frames, entries); returns the cels used."""
    items: list[dict[str, Any]] = tomllib.loads(src.read_text(encoding="utf-8"))["item"]
    rom = Rom()
    sheet = bytearray(sdd1.decompress(SHEET, SHEET_BYTES, rom)[0])
    for slot in SLOTS:
        for t in (slot, slot + 1, slot + 16, slot + 17):
            _put(sheet, t, bytes(TILE_BYTES))
    (out / "title_menu").mkdir(parents=True, exist_ok=True)
    slots, asm = iter(SLOTS), []
    for n, item in enumerate(items):
        grid = render([item["text"]], "menu", left=1)
        preview(grid).save(out / "title_menu" / f"{n}.png")
        old = rom.read(frame_at(rom, item["entry"]), 3)
        cels = [x for x in range(0, len(grid[0]), CEL) if any(v for row in grid for v in row[x : x + CEL])]
        records = [f"    .db 0x{0x80 | len(cels):02X}, 0x{old[1]:02X}, 0x{old[2]:02X}"]
        for x in cels:
            slot = next(slots, None)
            if slot is None:
                raise ValueError(f"title menu: {item['text']!r} needs more than the sheet's {len(SLOTS)} cels")
            for t, (dx, dy) in zip((slot, slot + 1, slot + 16, slot + 17), ((0, 0), (8, 0), (0, 8), (8, 8))):
                _put(sheet, t, tile(grid, x + dx, dy))
            records.append(f"    .db 1\n    .dw {x}, 0\n    .dw 0x{slot:04X}")
        name = f"title_menu_{n}"
        asm.append(f".alloc {name} in cutscene_frames {{\n" + "\n".join(records) + "\n}")
        asm.append(f".alloc at 0x{item['entry']:06X} size 2 {{\n    .dw {name} & 0xFFFF\n}}")
        asm.append(f'.assert {name} >> 16 == 0xCC, "{name}: sprite frames are read from bank CC"')
    (out / "title_sheet.bin").write_bytes(sdd1.compress(bytes(sheet)))
    asm.append('.alloc title_sheet in text16 {\n    .incbin "title_sheet.bin"\n}')
    asm.append(f".alloc at 0x{SHEET_ADDRESS:06X} size 2 {{\n    .dw title_sheet & 0xFFFF\n}}")
    asm.append(f".alloc at 0x{SHEET_BANK:06X} size 1 {{\n    .db title_sheet >> 16\n}}")
    (out / "title_menu.i").write_text("\n".join(asm) + "\n")
    return len(SLOTS) - sum(1 for _ in slots)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} cels")


if __name__ == "__main__":
    main()
