"""Seed the French dialog font: fonts/so_dialog.png and text/so_fr.tbl from FF4's 8x16 VWF font.

One-off: the png is the source afterwards (edit it, katsuji builds it). Its cell index is the stream code the
dialog uses: 0x00-0x04 are controls, a glyph is code - 5 as in the Japanese stream, and codes below 0x80 take one
byte. The Japanese layout keeps space at 0x05 and the digits at 0x06-0x0F (numbers are printed as digit + 1).
Characters FF4 has no glyph for are drawn here in its style: cap height rows 4-11, descenders to 13.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from tools.rom import ROOT

CELL_W, CELL_H, COLS, CELLS = 8, 16, 16, 256  # katsuji reads 256 cells; the patch keeps 0x00-0x7F
FF4 = Path.home() / "PyCharmProjects" / "ff4"
PNG = ROOT / "fonts" / "so_dialog.png"
TABLE = ROOT / "text" / "so_fr.tbl"

LAYOUT = (
    " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàâçèéêëîïôùûœÀÂÇÈÉÊËÎÏÔÙŒ.,!?'\":;-()*+/&>]○★☆♀♂♥♪"
)
FIRST_CODE = 0x05
# FF4 cells that are not in its table as these characters.
FF4_EXTRA = {'"': 0x92, "œ": 0xA0}

# Glyphs FF4 lacks: first row given, then one string per row.
DRAWN: dict[str, tuple[int, list[str]]] = {
    "(": (3, ["..#", ".#.", "#..", "#..", "#..", "#..", "#..", "#..", ".#.", "..#"]),
    ")": (3, ["#..", ".#.", "..#", "..#", "..#", "..#", "..#", "..#", ".#.", "#.."]),
    "*": (5, ["..#..", "#.#.#", ".###.", "#.#.#", "..#.."]),
    "+": (6, ["..#..", "..#..", "#####", "..#..", "..#.."]),
    "/": (4, ["...#", "...#", "..#.", "..#.", ".#..", ".#..", "#...", "#..."]),
    ";": (7, [".#", "..", "..", ".#", ".#", "#."]),
    "&": (4, [".##..", "#..#.", "#..#.", ".##..", "#.#.#", "#..#.", "#..##", ".##.#"]),
    ">": (6, ["#...", ".#..", "..#.", ".#..", "#..."]),
    "]": (3, ["###", "..#", "..#", "..#", "..#", "..#", "..#", "..#", "..#", "###"]),
    "Œ": (4, [".######", "#..#...", "#..#...", "#..####", "#..#...", "#..#...", "#..#...", ".######"]),
    "○": (5, [".###.", "#...#", "#...#", "#...#", ".###."]),
    "★": (4, ["...#...", "...#...", "#######", ".#####.", "..###..", ".##.##.", ".#...#."]),
    "☆": (4, ["...#...", "..#.#..", "###.###", "#.....#", ".#...#.", ".#.#.#.", "##...##"]),
    "♀": (4, [".###.", "#...#", "#...#", "#...#", ".###.", "..#..", "#####", "..#.."]),
    "♂": (4, ["..####", "....##", "...#.#", ".###..", "#...#.", "#...#.", "#...#.", ".###.."]),
    "♥": (5, [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]),
    "♪": (4, ["..#...", "..##..", "..#.#.", "..#..#", "..#...", ".##...", "###...", ".#...."]),
}


def ff4_cells(table: Path) -> dict[str, int]:
    cells = dict(FF4_EXTRA)
    for line in table.read_text(encoding="utf-8").splitlines():
        code, _, char = line.partition("=")
        if len(code) == 2 and len(char) == 1:
            cells.setdefault(char, int(code, 16))
    return cells


def drawn(char: str) -> Image.Image:
    top, rows = DRAWN[char]
    cell = Image.new("L", (CELL_W, CELL_H), 0)
    for y, row in enumerate(rows):
        for x, pixel in enumerate(row):
            if pixel == "#":
                cell.putpixel((x, top + y), 255)
    return cell


def seed(ff4_png: Path, ff4_table: Path) -> tuple[Image.Image, list[str]]:
    source, cells = Image.open(ff4_png).convert("L"), ff4_cells(ff4_table)
    atlas = Image.new("L", (COLS * CELL_W, CELLS // COLS * CELL_H), 0)
    lines = []
    for index, char in enumerate(LAYOUT):
        code = FIRST_CODE + index
        if char in DRAWN:
            cell = drawn(char)
        else:
            src = cells[char]
            x, y = src % COLS * CELL_W, src // COLS * CELL_H
            cell = source.crop((x, y, x + CELL_W, y + CELL_H))
        atlas.paste(cell, (code % COLS * CELL_W, code // COLS * CELL_H))
        lines.append(f"{code:02X}={char}")
    return atlas, lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ff4", type=Path, default=FF4, help="FF4 checkout (fonts/vwf.png, text/ff4fr.tbl)")
    args = ap.parse_args()
    if FIRST_CODE + len(LAYOUT) > 0x80:
        raise SystemExit(f"{len(LAYOUT)} glyphs do not fit below 0x80")
    atlas, lines = seed(args.ff4 / "fonts" / "vwf.png", args.ff4 / "text" / "ff4fr.tbl")
    atlas.convert("1").save(PNG)
    TABLE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(lines)} glyphs -> {PNG.relative_to(ROOT)}, {TABLE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
