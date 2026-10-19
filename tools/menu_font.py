"""The 8x8 menu font: fonts/so_menu8.png -> 2bpp tiles -> S-DD1, in place of the game's at DB:A078.

The png is 16 x 12 tiles of 8x8, 4 grey levels (0, 85, 170, 255 = colours 0-3); tile index = the byte in an 8x8
string (text/so_menu_fr.tbl). Codes C0-F2 draw a kana base tile with a dakuten on the row above (CA:BCAD): the
French table stays below C0. `--seed` makes the png from the old project's Font_8x8.bin (raw 2bpp).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from tools import sdd1
from tools.rom import ROOT

PNG = ROOT / "fonts" / "so_menu8.png"
OUT = ROOT / "build" / "gen" / "menu_font8.bin"
TILES, COLS = 192, 16
SIZE = TILES * 16  # bytes the five loaders DMA (0xC00)
SLOT = 1954  # the game's compressed stream at DB:A078
LEVEL = 85


def tiles_to_png(data: bytes) -> Image.Image:
    image = Image.new("L", (COLS * 8, TILES // COLS * 8))
    for tile in range(TILES):
        for y in range(8):
            low, high = data[tile * 16 + y * 2], data[tile * 16 + y * 2 + 1]
            for x in range(8):
                colour = (low >> (7 - x) & 1) | (high >> (7 - x) & 1) << 1
                image.putpixel((tile % COLS * 8 + x, tile // COLS * 8 + y), colour * LEVEL)
    return image


def png_to_tiles(image: Image.Image) -> bytes:
    grey = image.convert("L")
    out = bytearray()
    for tile in range(TILES):
        for y in range(8):
            low = high = 0
            for x in range(8):
                value = grey.getpixel((tile % COLS * 8 + x, tile // COLS * 8 + y))
                assert isinstance(value, int)  # "L": one channel
                colour = round(value / LEVEL)
                low |= (colour & 1) << (7 - x)
                high |= (colour >> 1) << (7 - x)
            out += bytes([low, high])
    return bytes(out)


def build(png: Path = PNG, out: Path = OUT) -> int:
    """Compressed size; the stream is padded to the game's slot."""
    packed = sdd1.compress(png_to_tiles(Image.open(png)))
    if len(packed) > SLOT:
        raise ValueError(f"{png.name}: {len(packed)} bytes compressed, DB:A078 holds {SLOT}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(packed + bytes(SLOT - len(packed)))
    return len(packed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=Path, help="old project's Font_8x8.bin: write the png from it")
    args = ap.parse_args()
    if args.seed:
        tiles_to_png(args.seed.read_bytes()[:SIZE]).save(PNG)
        print(f"{args.seed.name} -> {PNG.relative_to(ROOT)}")
    print(f"{build()} / {SLOT} bytes -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
