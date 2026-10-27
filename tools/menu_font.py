"""The 8x8 menu font: fonts/so_menu8.png -> 2bpp tiles -> S-DD1, in place of the game's at DB:A078.

The png is 16 x 12 tiles of 8x8, 4 grey levels (0, 85, 170, 255 = colours 0-3); tile index = the byte in an 8x8
string (text/so_menu_fr.tbl). Codes C0-F2 draw a kana base tile with a dakuten on the row above (CA:BCAD): the
French table stays below C0. `--seed` makes the png from the old project's Font_8x8.bin (raw 2bpp).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from katsuji import png
from katsuji.png import Pixels

from tools import sdd1
from tools.rom import ROOT

PNG = ROOT / "fonts" / "so_menu8.png"
OUT = ROOT / "build" / "gen" / "menu_font8.bin"
TILES, COLS = 192, 16
SIZE = TILES * 16  # bytes the five loaders DMA (0xC00)
SLOT = 1954  # the game's compressed stream at DB:A078
LEVEL = 85


def tiles_to_png(data: bytes) -> Pixels:
    """Grey pixels: 8-bit, one channel."""
    image = np.zeros((TILES // COLS * 8, COLS * 8), dtype=np.uint8)
    for tile in range(TILES):
        for y in range(8):
            low, high = data[tile * 16 + y * 2], data[tile * 16 + y * 2 + 1]
            for x in range(8):
                colour = (low >> (7 - x) & 1) | (high >> (7 - x) & 1) << 1
                image[tile // COLS * 8 + y, tile % COLS * 8 + x] = colour * LEVEL
    return image


def png_to_tiles(grey: Pixels) -> bytes:
    """`grey`: 8-bit, one channel, as `tiles_to_png` makes it."""
    if grey.ndim != 2:
        raise ValueError(f"menu font: grey pixels expected, got shape {grey.shape}")
    out = bytearray()
    for tile in range(TILES):
        for y in range(8):
            low = high = 0
            for x in range(8):
                colour = round(int(grey[tile // COLS * 8 + y, tile % COLS * 8 + x]) / LEVEL)
                low |= (colour & 1) << (7 - x)
                high |= (colour >> 1) << (7 - x)
            out += bytes([low, high])
    return bytes(out)


def build(png_path: Path = PNG, out: Path = OUT) -> int:
    """Compressed size; the stream is padded to the game's slot."""
    pixels, palette = png.read(png_path)
    if palette is not None:
        raise ValueError(f"{png_path.name}: palettized, the menu font is greyscale")
    packed = sdd1.compress(png_to_tiles(pixels))
    if len(packed) > SLOT:
        raise ValueError(f"{png_path.name}: {len(packed)} bytes compressed, DB:A078 holds {SLOT}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(packed + bytes(SLOT - len(packed)))
    return len(packed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=Path, help="old project's Font_8x8.bin: write the png from it")
    args = ap.parse_args()
    if args.seed:
        png.write(PNG, tiles_to_png(args.seed.read_bytes()[:SIZE]))
        print(f"{args.seed.name} -> {PNG.relative_to(ROOT)}")
    print(f"{build()} / {SLOT} bytes -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
