"""Dump the game fonts to PNG grids under extracted/fonts/."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from tools import sdd1
from tools.gfx import palette_image, tiles_image
from tools.rom import Rom

# Dialog / menu-window font: uncompressed, 16x16 1bpp, 32 B per glyph (cell index = glyph = code - 5).
DIALOG_FONT = 0xFF0000
DIALOG_GLYPHS = 0x640  # FF:C800 starts an LZ blob
GLYPH_BYTES = 32

# Menu 8x8 font: S-DD1 stream loaded to VRAM $2000 by CA:64EE. Tiles = ASCII 0x20-0x5F, kana after.
SMALL_FONT = 0xDBA078
SMALL_FONT_BYTES = 0xC00


def glyph_rows(data: bytes, g: int) -> list[int]:
    """16 rows of 16 bits: left column (16 B) then right column (16 B)."""
    o = g * GLYPH_BYTES
    return [data[o + y] << 8 | data[o + 16 + y] for y in range(16)]


def render(data: bytes, count: int, cols: int = 16) -> Image.Image:
    im = palette_image(cols * 16, -(-count // cols) * 16, 1)
    for g in range(count):
        for y, bits in enumerate(glyph_rows(data, g)):
            for x in range(16):
                if bits & 0x8000 >> x:
                    im.putpixel(((g % cols) * 16 + x, (g // cols) * 16 + y), 1)
    return im


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=Path("extracted/fonts"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    render(Rom().read(DIALOG_FONT, DIALOG_GLYPHS * GLYPH_BYTES), DIALOG_GLYPHS).save(args.out / "dialog_16x16.png")
    small, _ = sdd1.decompress(SMALL_FONT, SMALL_FONT_BYTES)
    tiles_image(small, 2, 16).save(args.out / "menu_8x8.png")
    print(f"{args.out}: dialog_16x16.png ({DIALOG_GLYPHS} glyphs), menu_8x8.png ({SMALL_FONT_BYTES // 16} tiles)")


if __name__ == "__main__":
    main()
