"""
Names (names8: party, items, skills, spells, enemies): French strings in place of the Japanese and of battle16's
(moved to the text16 pool), offset list D7:0000 rewritten (build/gen/names8.i, tools/encode_menus.py). C0:4B60
(build/gen/glyph_map.i) turns their 8x8 codes into 16x16 / dialog glyphs for the item panel and [item] inserts.
"""

.include "names8.i"
.include "glyph_map.i"

.import "core/preamble"

CLEAR_CELLS := 0xC045CA  ; X = tilemap offset, A = cells: blanks them in both battle shadows

; Battle: an enemy's name shows under it, centred and kept on its row (C1:4700), then C1:4797 / C1:47A6 blank 8
; cells from its start, on its row and the one above: the Japanese names' width. Blank to the row's end instead.
.alloc at 0xC14797 size 7 {
    jsl clear_to_row_end
    nop
    nop
    nop
}
.alloc at 0xC147A6 size 7 {
    jsl clear_to_row_end
    nop
    nop
    nop
}

.alloc battle_name_clear in code_c0 {
    .a16
    .i16
clear_to_row_end:
"""CLEAR_CELLS from X to the end of its 32-cell row."""
    txa
    lsr
    and.w #0x001F
    eor.w #0xFFFF
    clc
    adc.w #0x0021
    jml CLEAR_CELLS
}
