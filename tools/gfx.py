"""SNES planar tiles <-> palettized pixels for `katsuji.png`."""

from __future__ import annotations

import numpy as np
from katsuji.png import Pixels

Indexed = tuple[Pixels, tuple[int, ...]]  # colour indices and their flat RGB palette: `png.write(path, *indexed)`

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


def grey_palette(bpp: int) -> tuple[int, ...]:
    return tuple(g for g in GREYS[bpp] for _ in range(3))


def tiles_image(data: bytes, bpp: int, cols: int = 16) -> Indexed:
    """All tiles of ``data`` on a ``cols``-wide grid, palette index = pixel value."""
    n = len(data) // (8 * bpp)
    im = np.zeros((max(1, -(-n // cols)) * 8, cols * 8), dtype=np.uint8)
    for t in range(n):
        y, x = (t // cols) * 8, (t % cols) * 8
        im[y : y + 8, x : x + 8] = tile_pixels(data, t * 8 * bpp, bpp)
    return im, grey_palette(bpp)


def cells_image(
    data: bytes, bpp: int, cells_per_row: int, palette: list[tuple[int, int, int]] | None = None
) -> Indexed:
    """Text-window layout: each 8x16 cell is a top/bottom tile pair, cells left to right."""
    tile = 8 * bpp
    n = len(data) // (2 * tile)
    rows = max(1, -(-n // cells_per_row))
    im = np.zeros((rows * 16, cells_per_row * 8), dtype=np.uint8)
    for c in range(n):
        ox, oy = (c % cells_per_row) * 8, (c // cells_per_row) * 16
        for half in range(2):
            y = oy + half * 8
            im[y : y + 8, ox : ox + 8] = tile_pixels(data, (2 * c + half) * tile, bpp)
    return im, tuple(c for rgb in palette for c in rgb) if palette else grey_palette(bpp)
