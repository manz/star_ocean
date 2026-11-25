"""Outlined sprite lettering, shared by the fight popups (tools/battle_obj.py) and the command ring labels
(tools/ring_labels.py): glyphs as rows of `#`, laid out from column 1 with pair kerning, ink framed by a colour 1
outline on its four sides, on 8-row 4bpp tiles.
"""

from __future__ import annotations

Glyphs = dict[str, tuple[str, ...]]
Grid = list[list[int]]

ROWS = 8  # a word's height: 6 rows of letters (7 with an accent on top) between outline rows
OUTLINE = 1


def _edges(glyph: tuple[str, ...]) -> list[tuple[int, int] | None]:
    """Per canvas row, the first and last inked column (None for a blank row). A glyph sits on row 6."""
    top = ROWS - 1 - len(glyph)
    rows: list[tuple[int, int] | None] = [None] * ROWS
    for y, line in enumerate(glyph, top):
        if "#" in line:
            rows[y] = (line.index("#"), line.rindex("#"))
    return rows


def _kerned(reach: list[int | None], glyph: tuple[str, ...], at: int) -> int:
    """Leftmost start for `glyph` keeping a blank column between it and the ink so far, on its row and the rows next to
    it (letters touching on a diagonal read as one); never right of `at`."""
    pairs = [
        (last, edge[0])
        for y, edge in enumerate(_edges(glyph))
        if edge is not None
        for last in reach[max(0, y - 1) : y + 2]
        if last is not None
    ]
    return min(at, max((last + 2 - first for last, first in pairs), default=at))


def ink(text: str, glyphs: Glyphs) -> list[list[bool]]:
    """The word's ink, 8 rows, from column 1, each letter kerned: as far left as a blank column against its own and the
    next rows allows, never past a column after the previous letter's box."""
    rows = [[False] for _ in range(ROWS)]
    reach: list[int | None] = [None] * ROWS  # rightmost ink so far, per row
    for n, ch in enumerate(text):
        glyph = glyphs[ch]
        start = _kerned(reach, glyph, len(rows[0]) + 1) if n else len(rows[0])
        for row in rows:
            row.extend([False] * (start + len(glyph[0]) - len(row)))
        for y, edge in enumerate(_edges(glyph)):
            if edge is not None:
                line = glyph[y - (ROWS - 1 - len(glyph))]
                for x, c in enumerate(line):
                    if c == "#":
                        rows[y][start + x] = True
                reach[y] = start + edge[1]
    return rows


def paint(text: str, glyphs: Glyphs, width: int, top: int, bottom: int) -> Grid:
    """Colours of a `width`-pixel run: ink `top` on rows 0-3, `bottom` below, outlined, 0 around."""
    mask = ink(text, glyphs)
    used = len(mask[0])
    if used + 1 > width:
        raise ValueError(f"{text!r}: {used + 1} px, its run holds {width}")

    def inked(x: int, y: int) -> bool:
        return 0 <= x < used and 0 <= y < ROWS and mask[y][x]

    return [
        [
            (top if y <= 3 else bottom)
            if inked(x, y)
            else OUTLINE
            if any(inked(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            else 0
            for x in range(width)
        ]
        for y in range(ROWS)
    ]


def put(tile: bytearray, offset: int, x: int, y: int, colour: int) -> None:
    """Set pixel (x, y) of the 4bpp tile at `offset`."""
    bit = 7 - x
    for n, at in enumerate((y * 2, y * 2 + 1, 16 + y * 2, 16 + y * 2 + 1)):
        tile[offset + at] = tile[offset + at] & ~(1 << bit) | ((colour >> n) & 1) << bit
