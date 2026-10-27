"""Dump graphics that carry Japanese text, with their source pointers, to extracted/images/."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from katsuji import png

from tools import sdd1
from tools.gfx import bgr555, cells_image, tiles_image
from tools.rom import Rom

# C2:6791 reads 16-byte records: four 3-byte S-DD1 line pointers, a 3-byte pointer to the line
# palette (colours 1-3 at +2/+4/+6, loaded into $03E0-$03E5), one unused byte.
NARRATION_TABLE = 0xC2681A
NARRATION_SCREENS = 13
NARRATION_LINE_BYTES = 0x340  # 26 cells x (2 tiles x 16 B): one 208x16 2bpp line
BLANK_LINE = 0xE3FFF7


def narration(rom: Rom, out: Path) -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for screen in range(NARRATION_SCREENS):
        rec = rom.read(NARRATION_TABLE + screen * 16, 16)
        pal_ptr = int.from_bytes(rec[12:15], "little")
        palette = [(0, 0, 0)] + bgr555(rom.read(pal_ptr + 2, 6))
        for line in range(4):
            ptr = int.from_bytes(rec[line * 3 : line * 3 + 3], "little")
            if ptr == BLANK_LINE:
                continue
            data, packed = sdd1.decompress(ptr, NARRATION_LINE_BYTES)
            name = f"narration/{screen:02d}_{line}.png"
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            png.write(path, *cells_image(data, 2, 26, palette))
            entries.append(
                {
                    "file": name,
                    "codec": "sdd1",
                    "source": f"${ptr:06X}",
                    "rom_offset": rom.offset(ptr),
                    "packed_size": packed,
                    "size": NARRATION_LINE_BYTES,
                    "bpp": 2,
                    "layout": "cells26",
                    "table": f"${NARRATION_TABLE + screen * 16 + line * 3:06X}",
                    "palette": f"${pal_ptr:06X}",
                }
            )
    return entries


# Resist-screen element sprites with baked kanji (地 水 火 雷 風 光 闇 無 + 2 status icons): S-DD1 stream
# DMA'd to OBJ VRAM $7400 by CA:6533 (immediates, no table). 16x16 OBJ: tiles t, t+1 over t+16, t+17.
ELEMENT_SPRITES = 0xFE4B5B
ELEMENT_SPRITES_BYTES = 0x800


def element_sprites(rom: Rom, out: Path) -> list[dict[str, str | int]]:
    data, packed = sdd1.decompress(ELEMENT_SPRITES, ELEMENT_SPRITES_BYTES)
    name = "menu/element_sprites.png"
    (out / name).parent.mkdir(parents=True, exist_ok=True)
    png.write(out / name, *tiles_image(data, 4, 16))
    return [
        {
            "file": name,
            "codec": "sdd1",
            "source": f"${ELEMENT_SPRITES:06X}",
            "rom_offset": rom.offset(ELEMENT_SPRITES),
            "packed_size": packed,
            "size": ELEMENT_SPRITES_BYTES,
            "bpp": 4,
            "layout": "obj16x16",
            "site": "$CA6533",
            "palette": "OBJ, TBD",
        }
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=Path("extracted/images"))
    args = ap.parse_args()
    rom = Rom()
    entries = narration(rom, args.out) + element_sprites(rom, args.out)
    (args.out / "catalog.json").write_text(json.dumps(entries, indent=1))
    print(f"{len(entries)} images -> {args.out}")


if __name__ == "__main__":
    main()
