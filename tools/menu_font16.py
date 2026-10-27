"""The 16x16 menu font is the dialog font: build/gen/dialog_font.dat (katsuji, builtin sumi/16) -> the game's
1bpp glyphs at FF:0000, a width per glyph, and the 16x16 table.

Glyph g is dialog code g + 5 (so C0:4B60 serves the dialog [item] inserts and the 16x16 menus alike) and 16x16
code g + 0x10. FF:0000 + 32 g holds 16 rows of the left 8 columns then 16 of the right (empty: the dialog font is
8 px wide); `C8:0C3C` adds the outline. Width = the dialog advance: the VWF adds 1 px more for the outline.
"""

from __future__ import annotations

from pathlib import Path

from tools.rom import ROOT

GEN = ROOT / "build" / "gen"
DIALOG_FONT = GEN / "dialog_font.dat"
DIALOG_TABLE = ROOT / "text" / "so_fr.tbl"
TABLE = GEN / "so_menu16_fr.tbl"
RECORD, ROWS = 17, 16  # katsuji 8x16: 16 rows 1bpp + advance
DIALOG_BASE, DIALOG_END = 0x05, 0x80  # codes below 0x80 take one byte in the stream
BASE = 0x10  # 16x16 code of glyph 0
NEWLINE, END = 0x0D, 0xFF
GLYPHS = DIALOG_END - DIALOG_BASE
SPACE = BASE  # glyph 0
LINES, LINE_PIXELS = 3, 28 * 8  # src/menu/vwf16.s: the lines the description printer clears, and their width


def glyph(record: bytes) -> bytes:
    return record[:ROWS] + bytes(ROWS)


def width(record: bytes) -> int:
    return max(record[ROWS], 1)


def lines(codes: bytes, widths: bytes) -> int:
    """The lines the 16x16 description printer (src/menu/vwf16.s) sets terminated 16x16 codes on: a glyph advances
    its width + 1, a space breaks the line instead when it and the next word would pass LINE_PIXELS."""
    count, pixels = 1, 0
    for i, code in enumerate(codes):
        if code == END:
            break
        if code == NEWLINE:
            count, pixels = count + 1, 0
            continue
        if code == SPACE:
            word = codes[i + 1 :].split(bytes([END]))[0].replace(bytes([NEWLINE]), bytes([SPACE]))
            ahead = sum(widths[c - BASE] + 1 for c in bytes([SPACE]) + word.split(bytes([SPACE]))[0])
            if pixels + ahead > LINE_PIXELS:
                count, pixels = count + 1, 0
                continue
        pixels += widths[code - BASE] + 1
    return count


def table_lines(dialog_table: Path) -> list[str]:
    lines = [f"{NEWLINE:02X}=\\n"]
    for line in dialog_table.read_text(encoding="utf-8").splitlines():
        code, sep, text = line.partition("=")
        if sep and len(code) == 2 and DIALOG_BASE <= int(code, 16) < DIALOG_END:
            lines.append(f"{int(code, 16) - DIALOG_BASE + BASE:02X}={text}")
    return [*lines, f"{END:02X}=[end]"]


def build(out: Path = GEN, font: Path = DIALOG_FONT, dialog_table: Path = DIALOG_TABLE) -> int:
    """Writes menu_font16.bin, menu_font16_widths.bin and so_menu16_fr.tbl; returns the glyph count."""
    data = font.read_bytes()
    records = [data[(DIALOG_BASE + g) * RECORD : (DIALOG_BASE + g + 1) * RECORD] for g in range(GLYPHS)]
    out.mkdir(parents=True, exist_ok=True)
    (out / "menu_font16.bin").write_bytes(b"".join(glyph(r) for r in records))
    (out / "menu_font16_widths.bin").write_bytes(bytes(width(r) for r in records))
    (out / TABLE.name).write_text("\n".join(table_lines(dialog_table)) + "\n", encoding="utf-8")
    return GLYPHS
