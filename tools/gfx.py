"""SNES planar tiles <-> PIL images."""

from __future__ import annotations

from PIL import Image

GREYS = {1: [0, 255], 2: [0, 85, 170, 255], 4: [i * 17 for i in range(16)]}


def tile_pixels(data: bytes, offset: int, bpp: int) -> list[list[int]]:
    """Decode one 8x8 planar tile (2 planes interleaved per 16-byte block)."""
    rows = []
    for y in range(8):
        row = [0] * 8
        for plane in range(bpp):
            i = offset + (plane >> 1) * 16 + y * 2 + (plane & 1)
            b = data[i] if i < len(data) else 0
            for x in range(8):
                if b & 0x80 >> x:
                    row[x] |= 1 << plane
        rows.append(row)
    return rows


def bgr555(data: bytes) -> list[tuple[int, int, int]]:
    """SNES CGRAM words -> RGB888."""
    out = []
    for i in range(0, len(data) - 1, 2):
        w = data[i] | data[i + 1] << 8
        r, g, b = ((w >> s & 31) * 255 // 31 for s in (0, 5, 10))
        out.append((r, g, b))
    return out


def palette_image(width: int, height: int, bpp: int) -> Image.Image:
    im = Image.new("P", (width, height))
    pal = []
    for g in GREYS[bpp]:
        pal += [g, g, g]
    im.putpalette(pal)
    return im


def tiles_image(data: bytes, bpp: int, cols: int = 16) -> Image.Image:
    """All tiles of ``data`` on a ``cols``-wide grid, palette index = pixel value."""
    n = len(data) // (8 * bpp)
    im = palette_image(cols * 8, max(1, -(-n // cols)) * 8, bpp)
    for t in range(n):
        for y, row in enumerate(tile_pixels(data, t * 8 * bpp, bpp)):
            for x, v in enumerate(row):
                im.putpixel(((t % cols) * 8 + x, (t // cols) * 8 + y), v)
    return im


def cells_image(
    data: bytes, bpp: int, cells_per_row: int, palette: list[tuple[int, int, int]] | None = None
) -> Image.Image:
    """Text-window layout: each 8x16 cell is a top/bottom tile pair, cells left to right."""
    tile = 8 * bpp
    n = len(data) // (2 * tile)
    rows = max(1, -(-n // cells_per_row))
    im = palette_image(cells_per_row * 8, rows * 16, bpp)
    for c in range(n):
        ox, oy = (c % cells_per_row) * 8, (c // cells_per_row) * 16
        for half in range(2):
            for y, row in enumerate(tile_pixels(data, (2 * c + half) * tile, bpp)):
                for x, v in enumerate(row):
                    im.putpixel((ox + x, oy + half * 8 + y), v)
    if palette:
        im.putpalette([c for rgb in palette for c in rgb])
    return im
