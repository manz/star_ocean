"""Render the French cutscene text (text/fr/cutscenes.toml) as sprite frames for src/dialog/cutscenes.s.

The intro subtitles and credits are sprite frames (C3:8ECB): a 3-byte header (cel count, width / 4 - 1,
height / 4 - 1), then one record per cel: size (1 = 16x16), dx and dy (s16), a 24-bit source. A source in a
ROM bank is two 0x40-byte S-DD1 streams, the cel's top and bottom tile pairs, the second at source + the cel's
last byte (9-byte cel; the Japanese frames copy 0x80-byte cels from a WRAM sheet, 8-byte cels). Each French frame
is centred where the Japanese one was; the sprite-list word `entry` (bank CC) is repointed to it. The BG3 credit
titles (C2:DB33) are 256x16 2bpp streams, two 128-px halves; the credits script operands are repointed.
"""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from tools import sdd1
from tools.rom import ROOT, Rom

Grid = list[list[int]]

SCALE, CEL = 4, 16
# style -> font, px size, ground colour, darkest..brightest ink colours, blank cels kept (opaque ground)
STYLES: dict[str, tuple[Path, int, int, range, bool]] = {
    "subtitle": (Path("/System/Library/Fonts/Helvetica.ttc"), 12, 11, range(12, 16), True),
    "credit": (Path("/System/Library/Fonts/Times.ttc"), 13, 0, range(1, 4), False),
}
MAX_WIDTH = 256
LINE_STEP = 14  # credit lines
TITLE_BYTES = 0x400  # BG credit title (C2:DB33)


def render(lines: list[str], style: str, width: int = 0, left: int | None = None, right: int | None = None) -> Grid:
    """The lines on a grid of whole cels (or `width` px), as the style's colour indices: centred, or starting at
    `left`, or ending at `right`."""
    path, size, ground, inks, _ = STYLES[style]
    font = ImageFont.truetype(str(path), size * SCALE)
    widths = [font.getlength(line) / SCALE for line in lines]
    if max(widths) > MAX_WIDTH - 2:
        raise ValueError(f"cutscene line {lines[widths.index(max(widths))]!r} is {max(widths):.0f} px")
    width = width or -(-int(max(widths) + 2) // CEL) * CEL
    height = -(-(CEL + LINE_STEP * (len(lines) - 1)) // CEL) * CEL
    big = Image.new("L", (width * SCALE, height * SCALE))
    draw = ImageDraw.Draw(big)
    for i, (line, w) in enumerate(zip(lines, widths, strict=True)):
        x = left if left is not None else right - w if right is not None else (width - w) / 2
        if not 0 <= x <= width - w:
            raise ValueError(f"cutscene line {line!r} does not fit its {width} px")
        draw.text((round(x) * SCALE, (13 + i * LINE_STEP) * SCALE), line, font=font, fill=255, anchor="ls")
    small = big.resize((width, height), Image.Resampling.BOX).tobytes()
    levels = len(inks)
    return [
        [
            ground if v < 40 else inks[min(levels - 1, (v - 40) * levels // 216)]
            for v in small[y * width : (y + 1) * width]
        ]
        for y in range(height)
    ]


def tile(grid: Grid, x: int, y: int) -> bytes:
    """One 8x8 4bpp tile: planes 0-1 interleaved, then planes 2-3."""
    out = bytearray(32)
    for row in range(8):
        for col, v in enumerate(grid[y + row][x : x + 8]):
            for p in range(4):
                if v >> p & 1:
                    out[(p >> 1) * 16 + row * 2 + (p & 1)] |= 0x80 >> col
    return bytes(out)


def cels(grid: Grid, ground: int, keep_blank: bool) -> list[tuple[int, int, bytes, bytes]]:
    """(x, y, top stream, bottom stream) per 16x16 cel, blank ones dropped unless the ground is opaque."""
    out = []
    for y in range(0, len(grid), CEL):
        for x in range(0, len(grid[0]), CEL):
            if not keep_blank and all(v == ground for row in grid[y : y + CEL] for v in row[x : x + CEL]):
                continue
            top = tile(grid, x, y) + tile(grid, x + 8, y)
            bottom = tile(grid, x, y + 8) + tile(grid, x + 8, y + 8)
            out.append((x, y, sdd1.compress(top), sdd1.compress(bottom)))
    return out


def old_centre(rom: Rom, at: int) -> tuple[int, int, int]:
    """The Japanese frame's centre (x, y) and its byte size."""
    count, b1, b2 = rom.read(at, 3)
    return (b1 + 1) * 2, (b2 + 1) * 2, 3 + 8 * (count & 0x7F)


def tile2(grid: Grid, x: int, y: int) -> bytes:
    """One 8x8 2bpp tile."""
    out = bytearray(16)
    for row in range(8):
        for col, v in enumerate(grid[y + row][x : x + 8]):
            for p in range(2):
                if v >> p & 1:
                    out[row * 2 + p] |= 0x80 >> col
    return bytes(out)


def title_stream(grid: Grid) -> bytes:
    """A 256x16 BG credit title: two 128-px halves, each 16 tiles of the top row then 16 of the bottom."""
    return b"".join(
        tile2(grid, half * 128 + t * 8, row * 8) for half in range(2) for row in range(2) for t in range(16)
    )


def title_edges(rom: Rom, stream: int) -> tuple[int, int]:
    """First and last inked column of a Japanese title."""
    data, _ = sdd1.decompress(stream, TITLE_BYTES, rom)
    cols = {
        half * 128 + t * 8 + x
        for half in range(2)
        for row in range(2)
        for t in range(16)
        for y in range(8)
        for x in range(8)
        if data[half * 0x200 + row * 0x100 + t * 16 + y * 2] & 0x80 >> x
        or data[half * 0x200 + row * 0x100 + t * 16 + y * 2 + 1] & 0x80 >> x
    }
    return min(cols), max(cols)


def spans(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Half-open ranges, touching ones merged."""
    out: list[tuple[int, int]] = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(b, out[-1][1]))
        else:
            out.append((a, b))
    return out


def preview(grid: Grid) -> Image.Image:
    return Image.frombytes("L", (len(grid[0]), len(grid)), bytes(v * 17 for row in grid for v in row))


def build(src: Path = ROOT / "text" / "fr" / "cutscenes.toml", out: Path = ROOT / "build" / "gen") -> int:
    """cutscene_N_C_{top,bottom}.bin per cel, previews in cutscenes/, cutscenes.i (pool, frames, entries)."""
    doc = tomllib.loads(src.read_text(encoding="utf-8"))
    frames: list[dict[str, Any]] = doc["frame"]
    rom = Rom()
    (out / "cutscenes").mkdir(parents=True, exist_ok=True)
    reclaimed, asm = [], []
    for n, frame in enumerate(frames):
        style = frame.get("style", "subtitle")
        _, _, ground, _, keep_blank = STYLES[style]
        align = frame.get("align", "center")
        grid = render(frame["text"], style, left=1 if align == "left" else None)
        if align == "right":
            grid = render(frame["text"], style, width=len(grid[0]), right=len(grid[0]) - 1)
        preview(grid).save(out / "cutscenes" / f"{n:02d}.png")
        cx, cy, size = old_centre(rom, frame["at"])
        if not frame.get("keep"):
            reclaimed.append((frame["at"], frame["at"] + size))
        height, width = len(grid), len(grid[0])
        x0, y0 = {"left": (0, 0), "right": (cx * 2 - width, 0)}.get(align, (cx - width // 2, cy - height // 2))
        name = f"cutscene_{n:02d}"
        parts = cels(grid, ground, keep_blank)
        records = [f"    .db {len(parts)}, {width // 4 - 1:#04x}, {height // 4 - 1:#04x}"]
        for c, (x, y, top, bottom) in enumerate(parts):
            cel = f"{name}_{c:02d}"
            (out / f"{cel}_top.bin").write_bytes(top)
            (out / f"{cel}_bottom.bin").write_bytes(bottom)
            asm.append(f'.alloc {cel} in text16 {{\n    .incbin "{cel}_top.bin"\n    .incbin "{cel}_bottom.bin"\n}}')
            records.append(
                f"    .db 1\n    .dw {x0 + x} & 0xFFFF, {y0 + y} & 0xFFFF\n    .dl {cel}\n    .db {len(top)}"
            )
        asm.append(f".alloc {name} in cutscene_frames {{\n" + "\n".join(records) + "\n}")
        asm.append(f".alloc at 0x{frame['entry']:06X} size 2 {{\n    .dw {name} & 0xFFFF\n}}")
        asm.append(f'.assert {name} >> 16 == 0xCC, "{name}: sprite frames are read from bank CC"')
    for n, title in enumerate(doc.get("title", [])):
        first, last = title_edges(rom, title["at"])
        side = {"left": first} if title["align"] == "left" else {"right": last + 1}
        grid = render([title["text"]], "credit", width=256, **side)
        preview(grid).save(out / "cutscenes" / f"title_{n}.png")
        name = f"credit_title_{n}"
        (out / f"{name}.bin").write_bytes(sdd1.compress(title_stream(grid)))
        asm.append(f'.alloc {name} in text16 {{\n    .incbin "{name}.bin"\n}}')
        asm += [f".alloc at 0x{ptr:06X} size 3 {{\n    .dl {name}\n}}" for ptr in title["pointers"]]
    pool = [".pool cutscene_frames {", *(f"    range 0x{a:06X} 0x{b - 1:06X}" for a, b in spans(reclaimed))]
    pool += ["    range 0xCCFC60 0xCCFFFF", "    strategy pack", "}"]
    (out / "cutscenes.i").write_text("\n".join(pool + asm) + "\n")
    return len(frames)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "build" / "gen")
    print(f"{build(out=ap.parse_args().out)} frames")


if __name__ == "__main__":
    main()
