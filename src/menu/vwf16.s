"""
16x16 VWF, ported from the 2016 patch (menus_vwf_patch.s, display_description_text_reloc.s, status_reloc.s).

The three 16x16 printers (C6:F7D1 u16 buffer, C6:F6F9 menu16 by id, C6:F5FA battle16 by id) go to one pen:
`C8:0C3C` still blits a glyph into the two columns after the current one ($DB + 0x20), its tail now shifts them
right by the pen's pixel offset ($2E, 0-7) and ORs them into the current column; the pen then advances by the
glyph's width + 1 and every column it fills gets its two tilemap entries (tile 0x114 + $DD, $00 = attribute), as
the Japanese 12 px pairs did.

Printers: in X = tilemap address (row of the top tiles), $DB = column buffer offset in $7F, $DD = tile count,
$06 = palette. The battle copies in bank C0 (C0:48C6 u16 buffer, C0:460A battle16 by id) run the same pen in
battle mode: their blitter C0:46FB is C8:0C3C writing to $7E:D073 instead of $7F, X is an offset in the two
battle tilemap shadows ($7E:5100, $7E:5900) and the palette is $06 + 5. The menu buffer printer clears its three
lines first and wraps a line at a space when the next word would not fit; by-id strings are the text16 bytes
(src/menu/text16.s).
"""

.import "core/preamble"
.import "menu/text16"
.import "menu/font16"

.extern menu_font16_widths

COPY_CHAR := 0xC80C3C
BATTLE_COPY_CHAR := 0xC046FB  ; jsr only
BATTLE_BUFFER := 0xD073  ; its columns, in $7E
BATTLE_ROWS_1 := 0x7E5100  ; the two tilemap shadows the battle DMAs
BATTLE_ROWS_2 := 0x7E5900
BATTLE_PALETTE := 5
GLYPHS := 0x7B  ; tools/menu_font16.py: dialog codes 05-7F
GLYPH_BYTES := 32
WIDE_GAP := 8  ; advance of a glyph past the font
FIXED_WIDTH := 0x0B  ; name entry: 12 px cells
FIXED_PAD := 5  ; pen start in the name entry: a 5 px letter sits centred on its cell's square (pixels 3-11)
FIXED := 0xDEDE  ; $F0 while the name entry prints
BATTLE := 0xBA7E  ; $F0 while a battle copy prints
NAME_ROWS_1 := 0x3ACA  ; name entry tilemap addresses
NAME_ROWS_2 := 0x3B94  ; the nickname, at column 10 (CA:8E5E)
TILE_BASE := 0x0114
BLANK_TILE := 0x00C6  ; window background
LINE_ROWS := 0x80  ; tilemap bytes per 16 px line
COLUMNS := 30
LINES := 3
LINE_PIXELS := 28 * 8
NEWLINE := 0x000D
SPACE := 0x0010
END := 0xFFFF

pen = 0x2E  ; pixels of the current column used
attribute = 0x00
line_start = 0x22
column = 0xDB  ; offset of the current column in $7F
tile = 0xDD
mode = 0xF0
line_pixels = 0x7FFFFC  ; free: the 2016 patch kept it there

; copy_char tail: `lda 2E / beq / asl / tax / jsr (0D4B,x)` was the 12 px half shift.
.alloc at 0xC80D38 size 6 {
    jsr.w merge_glyph
    jmp.w 0x0D41
}

.macro merge(delta) {
    """New bytes at X + 0x20 + delta, shifted by the multiplier: low part stays, high part ORs into X + delta."""
    lda.w 0x0020 + delta, x
    sta.l 0x004203
    nop
    nop
    rep #0x20
    lda.l 0x004216
    sep #0x20
    sta.w 0x0020 + delta, x
    xba
    ora.w 0x0000 + delta, x
    sta.w 0x0000 + delta, x
}

; C0:47FD, the same tail in the battle blitter.
.alloc at 0xC047FD size 7 {
    jsl merge_glyph_battle
    jmp.w 0x4806
}

.alloc merge_glyph_battle in code_c8 {
"""merge_glyph over the battle columns in $7E."""
    sep #0x20
    lda.b #0x7E
    jsr.w merge_into
    rtl
}

.alloc merge_glyph in code_c8 {
"""Y = the glyph's first column (current + 0x20), M16 X16, DB = $C8. Out: DB = $7F."""
    sep #0x20
    lda.b #0x7F
    jsr.w merge_into
    rts
}

.alloc merge_into in code_c8 {
"""A (8 bits) = the columns' bank, Y = the glyph's first column (current + 0x20), X16. Out: DB = that bank."""
    pha
    plb
    rep #0x20
    tya
    sec
    sbc.w #0x0020
    tax  ; X = current column
    phy
    sep #0x20
    ldy.w #0x0020  ; bytes per column
    lda.b pen
    and.b #0x07
    beq _aligned
    phx
    rep #0x20
    and.w #0x0007
    tax
    sep #0x20
    lda.l shift_factor, x
    plx
    sta.l 0x004202
_shift:
    merge(0x00)
    merge(0x20)
    inx
    dey
    bne _shift
    ply
    rts
_aligned:
    lda.w 0x0020, x
    sta.w 0x0000, x
    lda.w 0x0040, x
    sta.w 0x0020, x
    inx
    dey
    bne _aligned
    ply
    rts
}

.alloc shift_factor in code_c8 {
"""Multiplier for a shift right by n: the high byte of byte * 2^(8 - n)."""
    .db 0x00, 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02
}

; ---- pen (M16 X16, X = tilemap address)

.alloc vwf16_width in code_c8 {
"""A = glyph -> A = its width in pixels."""
    cmp.w #GLYPHS
    bcs _past
    ldx.b mode
    cpx.w #FIXED
    beq _fixed
    tax
    lda.l menu_font16_widths, x
    and.w #0x00FF
    rts
_past:
    lda.w #WIDE_GAP
    rts
_fixed:
    lda.w #FIXED_WIDTH
    rts
}

.alloc vwf16_columns in code_c8 {
"""Emit the tilemap entries of every full column ($2E >= 8). Keeps Y."""
    phy
_next:
    lda.b pen
    cmp.w #8
    bcc _done
    lda.b tile
    clc
    adc.w #TILE_BASE
    clc
    adc.b attribute
    ldy.b mode
    cpy.w #BATTLE
    beq _battle
    sta.l 0x7E0000, x
    inc
    sta.l 0x7E0040, x
    bra _entered
_battle:
    sta.l BATTLE_ROWS_1, x
    sta.l BATTLE_ROWS_2, x
    inc
    sta.l BATTLE_ROWS_1 + 0x40, x
    sta.l BATTLE_ROWS_2 + 0x40, x
_entered:
    inc.b tile
    inc.b tile
    lda.b column
    clc
    adc.w #0x0020
    sta.b column
    inx
    inx
    lda.b pen
    sec
    sbc.w #8
    sta.b pen
    bra _next
_done:
    ply
    rts
}

.alloc vwf16_glyph in code_c8 {
"""A = code (0x10+): blit it at the pen, advance the pen. Keeps Y and DB."""
    sec
    sbc.w #0x0010
    pha
    phx
    phy
    phb
    asl
    asl
    asl
    asl
    asl
    tax  ; FF:0000 + 32 * glyph
    lda.b column
    clc
    adc.w #0x0020
    ldy.b mode
    cpy.w #BATTLE
    beq _battle
    tay
    lda.w #0x003F
    jsl COPY_CHAR
    bra _blitted
_battle:
    clc
    adc.w #BATTLE_BUFFER
    tay
    lda.w #0x003F
    jsl battle_copy_char
_blitted:
    plb
    ply
    plx
    pla
    phx
    jsr.w vwf16_width
    plx
    pha
    clc
    adc.b pen
    inc
    sta.b pen
    pla
    sec  ; + the 1 px gap
    adc.l line_pixels
    sta.l line_pixels
    jsr.w vwf16_columns
    rts
}

.alloc vwf16_flush in code_c8 {
"""Close the column the pen is in, if it holds anything."""
    lda.b pen
    beq _done
    lda.w #8
    sta.b pen
    jsr.w vwf16_columns
_done:
    stz.b pen
    rts
}

.alloc vwf16_newline in code_c8 {
    jsr.w vwf16_flush
    lda.w #0
    sta.l line_pixels
    lda.b line_start
    clc
    adc.w #LINE_ROWS
    sta.b line_start
    tax
    rts
}

.alloc vwf16_pen in code_c8 {
"""A = palette, X = tilemap address: pen at the line start, attribute."""
    stz.b pen
    xba
    and.w #0xFF00
    asl
    asl
    sta.b attribute
    stx.b line_start
    rts
}

.alloc battle_copy_char in code_c0 {
"""C0:46FB for the pen in bank C8."""
    jsr.w BATTLE_COPY_CHAR
    rtl
}

.alloc vwf16_setup_battle in code_c8 {
"""X = offset in the battle tilemap shadows: pen, attribute, line start, battle mode."""
    lda.b 0x06
    clc
    adc.w #BATTLE_PALETTE
    jsr.w vwf16_pen
    lda.w #0
    sta.l line_pixels
    lda.w #BATTLE
    sta.b mode
    rts
}

.alloc vwf16_setup in code_c8 {
"""A = anything, X = tilemap address: pen, attribute, line start, mode."""
    lda.b 0x06
    jsr.w vwf16_pen
    lda.w #0
    sta.l line_pixels
    stz.b mode
    cpx.w #NAME_ROWS_1
    beq _fixed
    cpx.w #NAME_ROWS_2
    bne _done
_fixed:
    jsl vwf16_setup_fixed
_done:
    rts
}

.alloc vwf16_setup_fixed in code_c4 {
"""Name entry mode, the pen FIXED_PAD in. The first glyph ORs into the column at $DB, so blank it. Keeps X and Y."""
    lda.w #FIXED
    sta.b mode
    lda.w #FIXED_PAD
    sta.b pen
    phx
    phy
    ldx.b column
    ldy.w #16
    lda.w #0
_blank:
    sta.l 0x7F0000, x
    inx
    inx
    dey
    bne _blank
    ply
    plx
    rtl
}

.alloc vwf16_clear in code_c8 {
"""Blank the three lines the buffer printer may use."""
    phx
    phy
    ldy.w #COLUMNS
    lda.w #BLANK_TILE
_next:
    .for line := 0, LINES {
        sta.l 0x7E0000 + line * LINE_ROWS, x
        sta.l 0x7E0040 + line * LINE_ROWS, x
    }
    inx
    inx
    dey
    bne _next
    ply
    plx
    rts
}

.alloc vwf16_word_fits in code_c8 {
"""Y at a space (u16 codes, DB = their bank): carry clear when the space and the next word fit the line."""
    phy
    lda.l line_pixels
    pha
    lda.w #SPACE - 0x10
    bra _add
_next:
    iny
    iny
    lda.w 0x0000, y
    cmp.w #END
    beq _test
    cmp.w #NEWLINE
    beq _test
    cmp.w #SPACE
    beq _test
    sec
    sbc.w #0x0010
_add:
    phx
    jsr.w vwf16_width
    plx
    inc
    clc
    adc.l line_pixels
    sta.l line_pixels
    bra _next
_test:
    lda.l line_pixels
    cmp.w #LINE_PIXELS + 1
    pla
    sta.l line_pixels
    ply
    rts
}

; ---- printers, entered by `jml` from their first bytes, M16 X16

; C6:F7D1, A = bank of the u16 codes, Y = their address (CA:BB07: item / skill descriptions).
.alloc at 0xC6F7D1 size 4 {
    jml.l vwf16_print_buffer
}

.alloc vwf16_print_buffer in code_c8 {
    php
    phb
    pei (mode)
    sep #0x20
    pha
    rep #0x20
    jsr.w vwf16_setup
    lda.b mode
    cmp.w #FIXED
    beq _start
    jsr.w vwf16_clear
_start:
    plb
_next:
    lda.w 0x0000, y
    cmp.w #END
    beq _end
    cmp.w #NEWLINE
    beq _newline
    cmp.w #SPACE
    bne _glyph
    jsr.w vwf16_word_fits
    lda.w #SPACE
    bcc _glyph
    jsr.w vwf16_newline
    bra _skip
_glyph:
    jsr.w vwf16_glyph
_skip:
    iny
    iny
    bra _next
_newline:
    jsr.w vwf16_newline
    bra _skip
_end:
    jsr.w vwf16_flush
    pla
    sta.b mode
    plb
    plp
    rtl
}

.macro print_by_id(ids, pointers, setup) {
    """A = string id, X = tilemap address: draw the text16 string, nothing when the id is unknown."""
    php
    phb
    pei (mode)
    rep #0x20
    sta.b 0x20
    jsr.w setup
    ldx.w #0
_find:
    lda.l ids, x
    beq _end
    cmp.b 0x20
    beq _found
    inx
    inx
    bra _find
_found:
    txa
    lsr
    sta.b 0x20
    txa
    clc
    adc.b 0x20
    tax  ; 3 * position
    sep #0x20
    lda.l pointers + 2, x
    pha
    plb
    rep #0x20
    lda.l pointers, x
    tay
    ldx.b line_start
_next:
    lda.w 0x0000, y
    and.w #0x00FF
    cmp.w #0x00FF
    beq _end
    cmp.w #NEWLINE
    beq _newline
    jsr.w vwf16_glyph
_skip:
    iny
    bra _next
_newline:
    jsr.w vwf16_newline
    bra _skip
_end:
    jsr.w vwf16_flush
    pla
    sta.b mode
    plb
    plp
    rtl
}

; C6:F6F9: menu16 by id (CA:BB02: help lines, titles).
.alloc at 0xC6F6F9 size 4 {
    jml.l vwf16_print_menu16
}

.alloc vwf16_print_menu16 in code_c8 {
    print_by_id(0x7F2000, menu16_pointers, vwf16_setup)
}

; C6:F5FA: battle16 by id (CA:BAFD), both of its 12 px and 8 px layouts.
.alloc at 0xC6F5FA size 4 {
    jml.l vwf16_print_battle16
}

.alloc vwf16_print_battle16 in code_c8 {
    print_by_id(0xD72A8D, battle16_pointers, vwf16_setup)
}

; C0:460A: battle16 by id in battle.
.alloc at 0xC0460A size 4 {
    jml.l vwf16_print_battle16_c0
}

.alloc vwf16_print_battle16_c0 in code_c8 {
    print_by_id(0xD72A8D, battle16_pointers, vwf16_setup_battle)
}

; C0:48C6, A = bank of the u16 codes, Y = their address (C1:7869: the battle message, a name + a battle16 string).
.alloc at 0xC048C6 size 4 {
    jml.l vwf16_print_battle_buffer
}

.alloc vwf16_print_battle_buffer in code_c8 {
    php
    phb
    pei (mode)
    sep #0x20
    pha
    rep #0x20
    jsr.w vwf16_setup_battle
    plb
_next:
    lda.w 0x0000, y
    cmp.w #END
    beq _end
    cmp.w #NEWLINE
    beq _newline
    jsr.w vwf16_glyph
_skip:
    iny
    iny
    bra _next
_newline:
    jsr.w vwf16_newline
    bra _skip
_end:
    jsr.w vwf16_flush
    pla
    sta.b mode
    plb
    plp
    rtl
}
