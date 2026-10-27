"""Redraw the town badge "PrivateAction" as "ActionPrivée" for src/dialog/badge.s.

The badge is a 48x16 sprite frame (C6:96E7, the C3:8ECB format: three 16x16 cels, each a top and a bottom 0x40-byte
S-DD1 stream back to back). Its letters are hand-drawn: tall capitals under a bar (rows 1-7) and 3-px lowercase
(rows 8-15). The French strip is put together from the Japanese one's own columns: the capitals swap places, the
bar is cut to fit between and after them, "riv" and "e" are kept, and é is e with an acute in rows 6-7.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from katsuji import png

from tools import sdd1
from tools.cutscene_text import preview, tile
from tools.gfx import tile_pixels
from tools.rom import ROOT, Rom

Grid = list[list[int]]

FRAME = 0xC696E7  # header, then three 9-byte cels: size, dx, dy, source, top stream size
CELS = 3
WIDTH, HEIGHT, SPLIT = 48, 16, 8  # SPLIT: first row of the lowercase
INK, GROUND = 15, 1
CEL_BYTES = 0x40
EDGE, EDGE_ROW = slice(44, 48), 5  # the right edge's columns, and a row where it runs straight


def cel_source(rom: Rom, cel: int) -> int:
    return int.from_bytes(rom.read(FRAME + 3 + cel * 9 + 5, 3), "little")


def original(rom: Rom) -> Grid:
    """The Japanese badge as colour indices."""
    grid = [[0] * WIDTH for _ in range(HEIGHT)]
    for cel in range(CELS):
        top, size = sdd1.decompress(cel_source(rom, cel), CEL_BYTES)
        bottom, _ = sdd1.decompress(cel_source(rom, cel) + size, CEL_BYTES)
        for half, data in enumerate((top, bottom)):
            for t in range(2):
                for y, row in enumerate(tile_pixels(data, t * 32, 4)):
                    grid[half * 8 + y][cel * 16 + t * 8 : cel * 16 + t * 8 + 8] = row
    return grid


def _columns(old: Grid, rows: range, picks: Sequence[int | None]) -> list[list[int]]:
    """Columns of `old` restricted to `rows` (None: a ground column)."""
    return [[GROUND] * len(rows) if c is None else [old[y][c] for y in rows] for c in picks]


def french(old: Grid) -> Grid:
    """ "ActionPrivée" out of "PrivateAction" (P cols 1-5, bar 6-25, A 26-28, bar and rounded end 29-47)."""
    upper = [0, *range(26, 29), 29, *[30] * 16, 24, 25, *range(1, 6), 6, 7, *[10] * 10, *range(40, 48)]
    lower = [0, *range(26, 29), *range(29, 47), 29, *range(1, 14), *range(22, 26), *range(22, 26), None, None, None, 47]
    columns = [a + b for a, b in zip(_columns(old, range(SPLIT), upper), _columns(old, range(SPLIT, HEIGHT), lower))]
    grid = [[columns[x][y] for x in range(WIDTH)] for y in range(HEIGHT)]
    grid[6][38] = grid[7][37] = INK  # the acute over the first e (cols 36-38)
    for y in range(EDGE_ROW + 1, HEIGHT - 1):  # the Japanese n ran under the edge: carry it down the freed columns
        grid[y][EDGE] = old[EDGE_ROW][EDGE]
    return grid


def streams(grid: Grid, cel: int) -> tuple[bytes, bytes]:
    """The cel's top and bottom tile pairs, compressed."""
    x = cel * 16
    top = tile(grid, x, 0) + tile(grid, x + 8, 0)
    bottom = tile(grid, x, 8) + tile(grid, x + 8, 8)
    return sdd1.compress(top), sdd1.compress(bottom)


def build(out: Path = ROOT / "build" / "gen") -> Grid:
    """badge_N.bin per cel, badge.png, badge.i (the cels in text16, the frame's sources repointed)."""
    grid = french(original(Rom()))
    out.mkdir(parents=True, exist_ok=True)
    png.write(out / "badge.png", preview(grid).repeat(4, 0).repeat(4, 1))
    asm = []
    for cel in range(CELS):
        top, bottom = streams(grid, cel)
        name = f"badge_{cel}"
        (out / f"{name}.bin").write_bytes(top + bottom)
        asm.append(f'.alloc {name} in text16 {{\n    .incbin "{name}.bin"\n}}')
        asm.append(f".alloc at 0x{FRAME + 3 + cel * 9 + 5:06X} size 4 {{\n    .dl {name}\n    .db {len(top)}\n}}")
    (out / "badge.i").write_text("\n".join(asm) + "\n")
    return grid


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    build(out=ap.parse_args().out)


if __name__ == "__main__":
    main()
