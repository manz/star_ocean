"""
The runtime 8x8 pen: a name typed in game (party names and nicknames, in RAM) drawn with katsuji's sumi/8
(build/gen/pen8.i, tools/pen8.py) into a vwf8 record (src/menu/vwf8.s) that its tiles upload from as they are.

A rendered name stays in SRAM, in one of PEN8_SLOTS slots keyed by its codes: the next draw of the same name, in a
menu, a fight or after a reset, finds it there. A slot is taken round robin; a name that changes takes a new one.
PEN8_MAGIC (the font's hash) tells a cache drawn by this font from bytes another build or a cold boot left.

Glyphs advance by their ink plus 1 pixel, the space by 3, then the menu font's shadow (1 pixel right, down and
diagonally) as the baked strings have. A name over more tiles than it has codes, or with a code sumi/8 does not
draw, is left to the game.
"""

.import "core/preamble"
.import "menu/text16"

.include "pen8.i"

PEN8_SLOTS := 12

_CODES := 7  ; a name's 6 codes and its end
_KEY := 8
_TILES := 6
_TILE_BYTES := 16
_SLOT_BYTES := _TILES * _TILE_BYTES
_RECORD := 16  ; tiles (3), tile count, cells, END
_WIDTH := 8  ; canvas bytes a row: 64 pixels
_GAP := 1
_SPACE_PX := 3
_END := 0xFF
_PARTY := 0x1548  ; 12 records of 12 bytes: name, nickname
_PARTY_END := 0x15D8
_ACTOR_NAMES := 0x708F  ; the actors' full names (field menus, the fight's command window), $100 apart, 8 actors
_ACTORS := 0x7097  ; and nicknames (the fight's party window)
_ACTOR_MASK := 0xF8FF

_record = 0x00
_string = 0x20

.struct Pen8 {
    word magic
    byte next  ; the slot the next new name takes
    byte slot
    byte fresh  ; 1: the slot was drawn by this call
    byte codes  ; the name's length
    word count  ; its tiles
    word x  ; pen position, pixels
    word width
    word glyph  ; row index in pen8_glyphs
    word column
    word bits
    word out  ; tile byte in pen8.tiles
    byte[PEN8_SLOTS * _KEY] key
    byte[PEN8_SLOTS * _RECORD] record
    byte[PEN8_SLOTS * _SLOT_BYTES] tiles
    byte[8 * _WIDTH] ink
    byte[8 * _WIDTH] shade
}

.reserve pen8 as Pen8 in sram

.alloc pen8_code in text16 {
    .a8
    .i16
pen8_find:
"""
The record of the name at $20-$22 (M8 X16): carry set, $00-$02 = the record, pen8.slot its slot, pen8.fresh 1 when
its tiles were drawn now. Carry clear: not a name, or one the game draws. X, Y and A clobbered.
"""
    lda.b _string + 2
    cmp.b #0x7E
    bne _refuse
    rep #0x20
    lda.b _string
    cmp.w #_PARTY
    bcc _actor
    cmp.w #_PARTY_END
    bcc _name
_actor:
    and.w #_ACTOR_MASK
    cmp.w #_ACTORS
    beq _name
    cmp.w #_ACTOR_NAMES
    beq _name
    sep #0x20
_refuse:
    clc
    rtl
_name:
    lda.l pen8.magic
    cmp.w #PEN8_MAGIC
    sep #0x20
    beq _length
    jsr.w _forget
_length:
    ldy.w #0
_measure:
    lda.b [_string], y
    cmp.b #_END
    beq _measured
    iny
    cpy.w #_CODES
    bcc _measure
    bra _refuse
_measured:
    tya
    beq _refuse
    sta.l pen8.codes
    lda.b #0
    sta.l pen8.slot
_probe:
    jsr.w _key_index
    ldy.w #0
_compare:
    lda.b [_string], y
    cmp.l pen8.key, x
    bne _other
    cmp.b #_END
    beq _hit
    inx
    iny
    bra _compare
_other:
    lda.l pen8.slot
    inc
    sta.l pen8.slot
    cmp.b #PEN8_SLOTS
    bcc _probe
    lda.l pen8.next
    sta.l pen8.slot
    inc
    cmp.b #PEN8_SLOTS
    bcc _next_slot
    lda.b #0
_next_slot:
    sta.l pen8.next
    jsr.w _render
    bcc _refuse
    lda.b #1
    bra _point
_hit:
    lda.b #0
_point:
    sta.l pen8.fresh
    rep #0x20
    lda.l pen8.slot
    and.w #0x00FF
    asl
    asl
    asl
    asl
    clc
    adc.w #pen8.record & 0xFFFF
    sta.b _record
    sep #0x20
    lda.b #pen8.record >> 16
    sta.b _record + 2
    sec
    rtl

_forget:
"""No name cached: SRAM another font or a cold boot left."""
    ldx.w #PEN8_SLOTS * _KEY - 1
    lda.b #_END
_forget_key:
    sta.l pen8.key, x
    dex
    bpl _forget_key
    lda.b #0
    sta.l pen8.next
    rep #0x20
    lda.w #PEN8_MAGIC
    sta.l pen8.magic
    sep #0x20
    rts

_key_index:
"""X = the slot's key."""
    rep #0x20
    lda.l pen8.slot
    and.w #0x00FF
    asl
    asl
    asl
    tax
    sep #0x20
    rts

_render:
"""The name into the slot's tiles, record and key: carry clear when the game must draw it (the key stays empty)."""
    jsr.w _key_index
    lda.b #_END
    sta.l pen8.key, x
    ldx.w #8 * _WIDTH - 1
    lda.b #0
_clear:
    sta.l pen8.ink, x
    dex
    bpl _clear
    rep #0x20
    lda.w #0
    sta.l pen8.x
    sep #0x20
    ldy.w #0
_code:
    lda.b [_string], y
    cmp.b #_END
    beq _inked
    cmp.b #PEN8_SPACE
    bne _letter
    rep #0x20
    lda.l pen8.x
    clc
    adc.w #_SPACE_PX
    sta.l pen8.x
    sep #0x20
    iny
    bra _code
_letter:
    cmp.b #PEN8_CODES
    bcs _fail
    phy
    jsr.w _glyph
    ply
    bcc _fail
    iny
    bra _code
_fail:
    clc
    rts
_inked:
    rep #0x20
    lda.l pen8.x
    clc
    adc.w #7
    lsr
    lsr
    lsr
    sta.l pen8.count
    sep #0x20
    cmp.l pen8.codes
    beq _fits
    bcs _fail
_fits:
    jsr.w _shadow
    jsr.w _tiles_out
    jsr.w _record_out
    jsr.w _key_index
    ldy.w #0
_key:
    lda.b [_string], y
    sta.l pen8.key, x
    inx
    iny
    cmp.b #_END
    bne _key
    sec
    rts

_glyph:
"""Code A's ink at pen8.x, the pen past it: carry clear when sumi/8 has no glyph for it or the canvas is full."""
    rep #0x20
    and.w #0x00FF
    tax
    asl
    asl
    asl
    sta.l pen8.glyph
    lda.l pen8_widths, x
    and.w #0x00FF
    bne _drawn
    jmp.w _no_glyph
_drawn:
    sta.l pen8.width
    clc
    adc.l pen8.x
    cmp.w #8 * _WIDTH - 8
    bcc _fits_canvas
    jmp.w _no_glyph
_fits_canvas:
    lda.l pen8.x
    lsr
    lsr
    lsr
    sta.l pen8.column
    ldy.w #0
_row:
    tya
    clc
    adc.l pen8.glyph
    tax
    lda.l pen8_glyphs, x
    and.w #0x00FF
    xba
    sta.l pen8.bits
    lda.l pen8.x
    and.w #7
    tax
    lda.l pen8.bits
_shift:
    dex
    bmi _shifted
    lsr
    bra _shift
_shifted:
    sta.l pen8.bits
    tya
    asl
    asl
    asl
    clc
    adc.l pen8.column
    tax
    sep #0x20
    lda.l pen8.bits + 1
    ora.l pen8.ink, x
    sta.l pen8.ink, x
    lda.l pen8.bits
    ora.l pen8.ink + 1, x
    sta.l pen8.ink + 1, x
    rep #0x20
    iny
    cpy.w #8
    bcc _row
    lda.l pen8.x
    clc
    adc.l pen8.width
    clc
    adc.w #_GAP
    sta.l pen8.x
    sep #0x20
    sec
    rts
_no_glyph:
    sep #0x20
    clc
    rts

_shadow:
"""pen8.shade: the ink, 1 pixel right of it, down and diagonally."""
    ldx.w #0
_spread:
    clc
    ldy.w #_WIDTH
_spread_byte:
    lda.l pen8.ink, x
    ror
    ora.l pen8.ink, x
    sta.l pen8.shade, x
    inx
    dey
    bne _spread_byte
    cpx.w #8 * _WIDTH
    bcc _spread
    ldx.w #8 * _WIDTH - 1
_down:
    lda.l pen8.shade - _WIDTH, x
    ora.l pen8.shade, x
    sta.l pen8.shade, x
    dex
    cpx.w #_WIDTH
    bcs _down
    rts

_tiles_out:
"""pen8.count 2bpp tiles into the slot: plane 0 the shade (ink and shadow), plane 1 the ink (colours 3 and 1)."""
    rep #0x20
    lda.l pen8.slot
    and.w #0x00FF
    sta.l pen8.out
    asl
    clc
    adc.l pen8.out  ; slot * 3
    asl
    asl
    asl
    asl
    asl  ; slot * _SLOT_BYTES
    sta.l pen8.out
    pha
    lda.w #0
    sta.l pen8.column
_tile:
    ldy.w #0
_tile_row:
    tya
    asl
    asl
    asl
    clc
    adc.l pen8.column
    tax
    sep #0x20
    lda.l pen8.ink, x
    xba
    lda.l pen8.shade, x
    rep #0x20
    pha
    lda.l pen8.out
    tax
    pla
    sta.l pen8.tiles, x
    inx
    inx
    txa
    sta.l pen8.out
    iny
    cpy.w #8
    bcc _tile_row
    lda.l pen8.column
    inc
    sta.l pen8.column
    cmp.l pen8.count
    bcc _tile
    pla
    sta.l pen8.out  ; the slot's first tile byte again
    sep #0x20
    rts

_record_out:
"""The slot's record: its tiles, their count, cells 1..count then blanks over the name's codes, END."""
    rep #0x20
    lda.l pen8.slot
    and.w #0x00FF
    asl
    asl
    asl
    asl
    tax
    lda.l pen8.out
    clc
    adc.w #pen8.tiles & 0xFFFF
    sta.l pen8.record, x
    sep #0x20
    lda.b #pen8.tiles >> 16
    sta.l pen8.record + 2, x
    lda.l pen8.count
    sta.l pen8.record + 3, x
    lda.b #1
_cell_out:
    pha
    cmp.l pen8.count
    beq _ink_cell
    bcc _ink_cell
    lda.b #0
_ink_cell:
    sta.l pen8.record + 4, x
    inx
    pla
    cmp.l pen8.codes
    beq _cells_done
    inc
    bra _cell_out
_cells_done:
    lda.b #_END
    sta.l pen8.record + 4, x
    rts
}
