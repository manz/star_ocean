"""Render the French narration screens (text/fr/narration.toml) into S-DD1 line streams for src/dialog/narration.s.

Each screen is a 208x64 2bpp picture cut into four 16-px lines (tools/dump_images.py: 26 cells, top tile then
bottom tile). The Calnus lines are white text on black, anti-aliased to the three grey colours of palette
`FE:FE03`. The letter (screen 0) keeps its parchment: the Japanese is erased from the original picture and the
French drawn over it in the ink colour. A line left empty is the game's blank line (`E3:FFF7`).
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path
from typing import Any

import numpy as np
from katsuji import png
from katsuji.png import Pixels
from PIL import Image, ImageChops, ImageDraw, ImageFont

from tools import sdd1
from tools.dump_images import BLANK_LINE, NARRATION_LINE_BYTES, NARRATION_SCREENS, NARRATION_TABLE
from tools.gfx import tile_pixels
from tools.rom import ROOT, Rom

Grid = list[list[int]]  # [y][x] colour indices or coverage

FONT = Path("/System/Library/Fonts/Helvetica.ttc")
SIZE, SCALE = 12, 4  # px; drawn SCALE times larger, then box-filtered down to grey levels
WIDTH, LINE, LINES = 208, 16, 4
HEIGHT = LINE * LINES
MARGIN = 4  # px kept clear on each side of a Calnus line
BASELINE, STEP = 13, 16  # the Japanese lines sit on y = 13 of their 16
LETTER_MARGIN = 10  # inside the torn edge
INK, CREASE, PAPER = 1, 2, 3  # letter colours (palette FE:FDFB)
PREVIEW = (0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255)


def coverage(screen: dict[str, Any], margin: int) -> Grid:
    """The screen's text as 0-255 coverage. A line starting with ">" is right-aligned."""
    font = ImageFont.truetype(str(FONT), SIZE * SCALE)
    canvas = Image.new("L", (WIDTH, HEIGHT))
    for i, line in enumerate(screen["text"]):
        if not line:
            continue
        align = "right" if line.startswith(">") else screen.get("align", "center")
        text = line.removeprefix(">")
        width = font.getlength(text) / SCALE
        if width > WIDTH - 2 * margin:
            raise ValueError(f"narration line {text!r} is {width:.0f} px, {WIDTH - 2 * margin} px fit")
        left = {"left": margin, "right": WIDTH - margin - width, "center": (WIDTH - width) / 2}[align]
        baseline = screen.get("baseline", BASELINE) + i * screen.get("step", STEP)
        big = Image.new("L", (WIDTH * SCALE, HEIGHT * SCALE))
        ImageDraw.Draw(big).text((round(left) * SCALE, baseline * SCALE), text, font=font, fill=255, anchor="ls")
        canvas = ImageChops.lighter(canvas, big.resize((WIDTH, HEIGHT), Image.Resampling.BOX))
    flat = canvas.tobytes()
    return [list(flat[y * WIDTH : (y + 1) * WIDTH]) for y in range(HEIGHT)]


def original(rom: Rom, screen: int) -> Grid:
    """The Japanese screen as colour indices."""
    grid = [[0] * WIDTH for _ in range(HEIGHT)]
    for line in range(LINES):
        ptr = int.from_bytes(rom.read(NARRATION_TABLE + screen * 16 + line * 3, 3), "little")
        if ptr == BLANK_LINE:
            continue
        data, _ = sdd1.decompress(ptr, NARRATION_LINE_BYTES)
        for tile in range(NARRATION_LINE_BYTES // 16):
            ox, oy = tile // 2 * 8, line * LINE + tile % 2 * 8
            for y, row in enumerate(tile_pixels(data, tile * 16, 2)):
                grid[oy + y][ox : ox + 8] = row
    return grid


def around(grid: Grid, x: int, y: int, r: int) -> list[int]:
    return [
        grid[j][i]
        for j in range(max(0, y - r), min(HEIGHT, y + r + 1))
        for i in range(max(0, x - r), min(WIDTH, x + r + 1))
    ]


def erase_ink(grid: Grid) -> Grid:
    """The parchment without its writing: ink away from the torn edge takes the paper colour around it."""
    ink = [(x, y) for y in range(HEIGHT) for x in range(WIDTH) if grid[y][x] == INK and 0 not in around(grid, x, y, 1)]
    while ink:
        left = []
        for x, y in ink:
            near = [v for v in around(grid, x, y, 2) if v in (CREASE, PAPER)]
            if near:
                grid[y][x] = max(set(near), key=near.count)
            else:
                left.append((x, y))
        if len(left) == len(ink):
            for x, y in left:
                grid[y][x] = PAPER
            break
        ink = left
    return grid


def letter(rom: Rom, screen: dict[str, Any]) -> Grid:
    grid = erase_ink(original(rom, 0))
    cover = coverage(screen, LETTER_MARGIN)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] and cover[y][x] >= 112:
                grid[y][x] = INK
    return grid


def calnus(screen: dict[str, Any]) -> Grid:
    return [[min(3, (v + 40) // 80) for v in row] for row in coverage(screen, MARGIN)]


def cells(grid: Grid, line: int) -> bytes:
    """One 16-px line as 26 cells of top and bottom 2bpp tiles."""
    out = bytearray()
    for cell in range(WIDTH // 8):
        for y in range(line * LINE, line * LINE + LINE):
            planes = [0, 0]
            for x, v in enumerate(grid[y][cell * 8 : cell * 8 + 8]):
                for p in range(2):
                    planes[p] |= (v >> p & 1) << (7 - x)
            out += bytes(planes)
    return bytes(out)


def preview(grid: Grid) -> tuple[Pixels, tuple[int, ...]]:
    """Colour indices and their palette, for `png.write`."""
    return np.array(grid, dtype=np.uint8), PREVIEW


def build(src: Path = ROOT / "text" / "fr" / "narration.toml", out: Path = ROOT / "build" / "gen") -> int:
    """narration_SS_L.bin per drawn line, previews in narration/, narration.i (allocs, table); returns the lines."""
    screens = tomllib.loads(src.read_text(encoding="utf-8"))["screen"]
    if len(screens) != NARRATION_SCREENS:
        raise ValueError(f"{src}: {len(screens)} screens, the game has {NARRATION_SCREENS}")
    rom = Rom()
    (out / "narration").mkdir(parents=True, exist_ok=True)
    asm, lines = [], 0
    for s, screen in enumerate(screens):
        grid = letter(rom, screen) if s == 0 else calnus(screen)
        png.write(out / "narration" / f"{s:02d}.png", *preview(grid))
        for line in range(LINES):
            data = cells(grid, line)
            entry = f"0x{NARRATION_TABLE + s * 16 + line * 3:06X}"
            if not any(data):
                asm.append(f".alloc at {entry} size 3 {{\n    .dl 0x{BLANK_LINE:06X}\n}}")
                continue
            name = f"narration_{s:02d}_{line}"
            (out / f"{name}.bin").write_bytes(sdd1.compress(data))
            asm.append(f'.alloc {name} in text16 {{\n    .incbin "{name}.bin"\n}}')
            asm.append(f".alloc at {entry} size 3 {{\n    .dl {name}\n}}")
            lines += 1
    (out / "narration.i").write_text("\n".join(asm) + "\n")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} lines")


if __name__ == "__main__":
    main()
