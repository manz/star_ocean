"""Redraw the はい / いいえ choice bubbles as "Oui" / "Non" for src/dialog/yes_no.s.

Each answer has two sprite frames (the C3:8ECB format): a large 48x24 bubble for the selected answer, a small 32x16
one for the other. A frame is a 3-byte header (cel count, width / 4 - 1, height / 4 - 1), then one record per cel:
size, dx and dy (s16), a 24-bit source. A 16x16 cel (9-byte record) is a top and a bottom 0x40-byte S-DD1 stream,
the bottom one at source + the record's last byte; an 8x8 cel (8-byte record) is one 0x20-byte stream.

The letters are bright strokes on the bubble's ground with a shade dropped left and down: 2 px strokes and shade
on the large bubble, 1 px on the small one. The Japanese letters are wiped off (the rim kept) and the French drawn
in the same style, centred on the bubble's inside.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from tools import sdd1
from tools.cutscene_text import preview, tile
from tools.gfx import tile_pixels
from tools.rom import ROOT, Rom

Grid = list[list[int]]

GROUND, SHADE, INK = 13, 14, 15

# fmt: off
LARGE_GLYPHS = {
    "O": ("..######..", ".########.", "###....###", "##......##", "##......##", "##......##",
          "##......##", "##......##", "##......##", "###....###", ".########.", "..######.."),
    "N": ("##......##", "###.....##", "####....##", "##.##...##", "##.##...##", "##..##..##",
          "##..##..##", "##...##.##", "##...##.##", "##....####", "##.....###", "##......##"),
    "u": ("##....##", "##....##", "##....##", "##....##", "##....##", "##...###", "########", ".####.##"),
    "o": (".######.", "########", "##....##", "##....##", "##....##", "##....##", "########", ".######."),
    "n": ("##.####.", "########", "###...##", "##....##", "##....##", "##....##", "##....##", "##....##"),
    "i": ("##", "##", "..", "..", "##", "##", "##", "##", "##", "##", "##", "##"),
}
SMALL_GLYPHS = {
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "u": ("#..#", "#..#", "#..#", "#..#", ".###"),
    "o": (".##.", "#..#", "#..#", "#..#", ".##."),
    "n": ("###.", "#..#", "#..#", "#..#", "#..#"),
    "i": ("#", ".", "#", "#", "#", "#", "#"),
}
# fmt: on


@dataclass(frozen=True)
class Style:
    glyphs: dict[str, tuple[str, ...]]
    baseline: int  # last row of the letters (they sit on it, capitals rising above the lowercase)
    gap: int  # between letters: the next one's shade takes part of it
    shadow: tuple[tuple[int, int], ...]  # a ground pixel is shade when ink sits at +dx, +dy
    text_rows: range  # rows the Japanese letters and their shade cover
    rim_shade: int  # at most this many shade pixels inside the outline belong to the rim

    @property
    def shade_width(self) -> int:
        return max(dx for dx, _ in self.shadow)


LARGE = Style(LARGE_GLYPHS, 16, 3, ((2, 0), (2, -1), (1, 0), (1, -1), (0, -1)), range(4, 19), 3)
SMALL = Style(SMALL_GLYPHS, 10, 2, ((1, 0), (1, -1), (0, -1)), range(3, 13), 1)


@dataclass(frozen=True)
class Bubble:
    name: str
    frame: int
    word: str
    style: Style


BUBBLES = (
    Bubble("yes", 0xC42409, "Oui", LARGE),
    Bubble("no", 0xC42457, "Non", LARGE),
    Bubble("yes_small", 0xC422F2, "Oui", SMALL),
    Bubble("no_small", 0xC42307, "Non", SMALL),
)


@dataclass(frozen=True)
class Cel:
    size: int  # 1: 16x16, two 0x40 streams; 0: 8x8, one 0x20 stream
    dx: int
    dy: int
    record: int  # ROM address of its record in the frame


def dimensions(rom: Rom, frame: int) -> tuple[int, int]:
    _, width, height = rom.read(frame, 3)
    return (width + 1) * 4, (height + 1) * 4


def cels(rom: Rom, frame: int) -> list[Cel]:
    count, at, out = rom.read(frame, 1)[0], frame + 3, []
    for _ in range(count):
        size, dx, dy = rom.read(at, 1)[0], *(int.from_bytes(rom.read(at + o, 2), "little", signed=True) for o in (1, 3))
        out.append(Cel(size, dx, dy, at))
        at += 9 if size else 8
    return out


def source(rom: Rom, cel: Cel) -> int:
    return int.from_bytes(rom.read(cel.record + 5, 3), "little")


def original(rom: Rom, frame: int) -> Grid:
    """The Japanese bubble as colour indices."""
    width, height = dimensions(rom, frame)
    grid = [[0] * width for _ in range(height)]
    for cel in cels(rom, frame):
        if cel.size:  # the record's last byte: where the bottom stream starts
            top, _ = sdd1.decompress(source(rom, cel), 0x40)
            bottom, _ = sdd1.decompress(source(rom, cel) + rom.read(cel.record + 8, 1)[0], 0x40)
            tiles = [(top, 0, 0, 0), (top, 32, 8, 0), (bottom, 0, 0, 8), (bottom, 32, 8, 8)]
        else:
            tiles = [(sdd1.decompress(source(rom, cel), 0x20)[0], 0, 0, 0)]
        for data, offset, tx, ty in tiles:
            for y, row in enumerate(tile_pixels(data, offset, 4)):
                grid[cel.dy + ty + y][cel.dx + tx : cel.dx + tx + 8] = row
    return grid


def blank(old: Grid, style: Style) -> Grid:
    """The bubble with its letters wiped: each text row is ground between the rim (outline + its shade)."""
    grid = [row[:] for row in old]
    for y in style.text_rows:
        row = old[y]
        left = next(x for x, v in enumerate(row) if v > 1)
        left += next((n for n in range(style.rim_shade) if row[left + n] != SHADE), style.rim_shade)
        right = max(x for x, v in enumerate(row) if v > 1)
        right -= next((n for n in range(style.rim_shade) if row[right - n] != SHADE), style.rim_shade)
        grid[y][left : right + 1] = [GROUND] * (right - left + 1)
    return grid


def ink(word: str, style: Style, ground: list[int]) -> set[tuple[int, int]]:
    """The word's ink pixels, it and its shade centred on the `ground` columns (the bubble's inside)."""
    width = sum(len(style.glyphs[c][0]) for c in word) + style.gap * (len(word) - 1) + style.shade_width
    x = ground[0] + (len(ground) - width + 1) // 2 + style.shade_width
    out = set()
    for c in word:
        rows = style.glyphs[c]
        top = style.baseline + 1 - len(rows)
        out |= {(x + i, top + j) for j, row in enumerate(rows) for i, v in enumerate(row) if v == "#"}
        x += len(rows[0]) + style.gap
    return out


def french(old: Grid, bubble: Bubble) -> Grid:
    style = bubble.style
    grid = blank(old, style)
    middle = grid[(style.text_rows.start + style.baseline) // 2]
    pixels = ink(bubble.word, style, [x for x, v in enumerate(middle) if v == GROUND])
    for x, y in pixels:
        grid[y][x] = INK
    for x, y in {(x - dx, y - dy) for x, y in pixels for dx, dy in style.shadow} - pixels:
        if grid[y][x] == GROUND:
            grid[y][x] = SHADE
    return grid


def streams(grid: Grid, cel: Cel) -> list[bytes]:
    """The cel's streams, compressed: top and bottom tile pairs for a 16x16, the one tile for an 8x8."""
    if cel.size:
        top = tile(grid, cel.dx, cel.dy) + tile(grid, cel.dx + 8, cel.dy)
        bottom = tile(grid, cel.dx, cel.dy + 8) + tile(grid, cel.dx + 8, cel.dy + 8)
        return [sdd1.compress(top), sdd1.compress(bottom)]
    return [sdd1.compress(tile(grid, cel.dx, cel.dy))]


def asm(name: str, cel: Cel, parts: list[bytes]) -> list[str]:
    """The cel's streams in text16, and its record's source (and bottom stream offset) repointed to them."""
    record = f".dl {name}\n    .db {len(parts[0])}" if cel.size else f".dl {name}"
    return [
        f'.alloc {name} in text16 {{\n    .incbin "{name}.bin"\n}}',
        f".alloc at 0x{cel.record + 5:06X} size {4 if cel.size else 3} {{\n    {record}\n}}",
    ]


def build(out: Path = ROOT / "build" / "gen") -> dict[str, Grid]:
    """yes_no_<bubble>_N.bin per cel, yes_no.png, yes_no.i."""
    rom = Rom()
    out.mkdir(parents=True, exist_ok=True)
    grids, lines = {}, []
    for bubble in BUBBLES:
        grid = grids[bubble.name] = french(original(rom, bubble.frame), bubble)
        for n, cel in enumerate(cels(rom, bubble.frame)):
            parts = streams(grid, cel)
            name = f"yes_no_{bubble.name}_{n}"
            (out / f"{name}.bin").write_bytes(b"".join(parts))
            lines += asm(name, cel, parts)
    sheet = Image.new("L", (max(len(g[0]) for g in grids.values()), sum(len(g) for g in grids.values())))
    y = 0
    for grid in grids.values():
        sheet.paste(preview(grid), (0, y))
        y += len(grid)
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.Resampling.NEAREST).save(out / "yes_no.png")
    (out / "yes_no.i").write_text("\n".join(lines) + "\n")
    return grids


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    build(out=ap.parse_args().out)


if __name__ == "__main__":
    main()
