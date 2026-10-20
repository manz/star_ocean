"""
8x8 VWF for the names8 strings (spike: item, skill and spell lists). tools/names8_vwf.py bakes each string as a
proportional strip of 2bpp tiles, one S-DD1 stream each, and a table by names8 position (`names8_vwf`: 24-bit
stream, tile count). The names8 printer's draw (`CA:A690 jsr BC2E`, $20 = the D7 offset-list entry, $24 = the
tilemap shadow address, $26 = attribute, $27 = the field's cells) goes through `vwf8_name` first: a baked string
takes free pool tiles, its stream is queued for the frame's upload (`CA:6CD1`, after the game's own) and the
field gets the tile ids; anything else is drawn by the game.

Pool: tiles POOL_FIRST-POOL_LAST of the menus' BG1-3 CHR ($2000). A tile is free when none of the three tilemap
shadows ($7E:3100/3900/4100) uses it, scanned once per frame, and nothing took it since.
"""

.import "core/preamble"
.import "menu/text16"

.include "names8_vwf.i"

_POOL_FIRST := 0x300
_POOL_LAST := 0x3EF
_POOL_TILES := _POOL_LAST - _POOL_FIRST + 1
_QUEUE_SLOTS := 24
_SLOT := 6  ; stream (3), bytes (1), VRAM word (2)
_SHADOWS := 0x7E3100  ; three 0x800-byte maps
_SHADOW_BYTES := 0x1800
_CHR := 0x2000
_BLIT := 0xCABC2E

_src = 0x20  ; the names8 offset-list entry (D7:0000 + position * 2)
_src_bank = 0x22  ; 0: names8
_cursor = 0x24  ; tilemap shadow address of the field's first cell
_attribute = 0x26
_cells = 0x27

.struct Vwf8 {
    byte queued
    byte frame  ; counts uploads
    byte scanned  ; frame at the last scan
    word first  ; the tile vwf8_allocate found
    byte count  ; the string's tiles
    byte[_QUEUE_SLOTS * _SLOT] queue
    byte[_POOL_TILES] used  ; 1: a map shows it
}

.reserve vwf8 as Vwf8 in sram

; The names8 printer's draw.
.alloc at 0xCAA690 size 3 {
    jsr.w vwf8_cave_name
}

; The frame's upload, after the game's $7F slot: `lda #0x20 / trb 0601`.
.alloc at 0xCA6CD1 size 5 {
    jsr.w vwf8_cave_drain
    nop
    nop
}

; The two menu font loads (`ldx #0xA078`, the stream's address): a menu opens, the pool starts over.
.alloc at 0xCA64CD size 3 {
    jsr.w vwf8_cave_open
}
.alloc at 0xCA6832 size 3 {
    jsr.w vwf8_cave_open
}

.alloc vwf8_caves at 0xCAFF8C size 0x1C {
vwf8_cave_open:
    jsl vwf8_open
    ldx.w #0xA078
    rts

vwf8_cave_name:
    jsl vwf8_name
    bcs _drawn
    jsr.w _BLIT & 0xFFFF
_drawn:
    rts

vwf8_cave_drain:
    jsl vwf8_drain
    lda.b #0x20
    trb.w 0x0601
    rts
}

.alloc vwf8_code in code_c6 {
    .a8
    .i16
vwf8_name:
"""A baked names8 string into the field: carry set when drawn, clear for the game to draw it."""
    lda.b _src_bank
    bne _game
    rep #0x30
    lda.b _src
    asl
    tax
    lda.l names8_vwf + 3, x
    and.w #0x00FF
    beq _game16
    sep #0x20
    cmp.b _cells
    beq _fits
    bcs _game
_fits:
    sta.l vwf8.count
    jsr.w _allocate
    bcc _game
    jsr.w _enqueue
    bcc _game
    jsr.w _fill
    sec
    rtl
_game16:
    sep #0x20
_game:
    clc
    rtl

_allocate:
"""vwf8.count contiguous free pool tiles: vwf8.first = the first (tile number), carry clear when full."""
    lda.l vwf8.frame
    cmp.l vwf8.scanned
    beq _search
    sta.l vwf8.scanned
    jsr.w _scan
_search:
    ldx.w #0
_start:
    ldy.w #0
_run:
    lda.l vwf8.used, x
    bne _taken
    iny
    inx
    tya
    cmp.l vwf8.count
    beq _found
    cpx.w #_POOL_TILES
    bcc _run
    clc
    rts
_taken:
    inx
    cpx.w #_POOL_TILES
    bcc _start
    clc
    rts
_found:
    txa
    sec
    sbc.l vwf8.count
    rep #0x20
    and.w #0x00FF
    tax
    clc
    adc.w #_POOL_FIRST
    sta.l vwf8.first
    sep #0x20
    rep #0x20
    lda.l vwf8.count
    and.w #0x00FF
    tay
    sep #0x20
    lda.b #1
_mark:
    sta.l vwf8.used, x
    inx
    dey
    bne _mark
    sec
    rts

_scan:
"""vwf8.used from the shadows: a pool tile is taken when a map shows it (the fill writes its tiles at once)."""
    ldx.w #_POOL_TILES - 1
    lda.b #0
_clear:
    sta.l vwf8.used, x
    dex
    bpl _clear
    rep #0x20
    ldx.w #0
_entry:
    lda.l _SHADOWS, x
    and.w #0x03FF
    sec
    sbc.w #_POOL_FIRST
    cmp.w #_POOL_TILES
    bcs _next
    phx
    tax
    sep #0x20
    lda.b #1
    sta.l vwf8.used, x
    rep #0x20
    plx
_next:
    inx
    inx
    cpx.w #_SHADOW_BYTES
    bcc _entry
    sep #0x20
    rts

_enqueue:
"""The string's stream for the next upload into vwf8.first's _CHR: carry clear when the queue is full."""
    lda.l vwf8.queued
    cmp.b #_QUEUE_SLOTS
    bcs _full
    rep #0x20
    and.w #0x00FF
    sta.b 0x00
    asl
    adc.b 0x00
    asl
    tay  ; slot offset
    lda.b _src
    asl
    tax
    lda.l names8_vwf, x
    phx
    tyx
    sta.l vwf8.queue, x
    plx
    lda.l names8_vwf + 2, x
    tyx
    sta.l vwf8.queue + 2, x  ; bank, then the byte count below
    lda.l vwf8.first
    asl
    asl
    asl
    clc
    adc.w #_CHR
    sta.l vwf8.queue + 4, x
    sep #0x20
    lda.l vwf8.count
    asl
    asl
    asl
    asl
    sta.l vwf8.queue + 3, x
    lda.l vwf8.queued
    inc
    sta.l vwf8.queued
    sec
    rts
_full:
    clc
    rts

_fill:
"""The field's _cells: the strip's tiles, then blanks; the row above (accents in the game's font) blank."""
    rep #0x20
    ldx.b _cursor
    lda.l vwf8.first
    sta.b 0x00
    sep #0x20
    lda.l vwf8.count
    sta.b 0x02
    lda.b _cells
    sta.b 0x03
_cell:
    lda.b #0
    sta.l 0x7DFFC0, x
    sta.l 0x7DFFC1, x
    lda.b 0x02
    beq _blank
    dec.b 0x02
    lda.b 0x00
    sta.l 0x7E0000, x
    lda.b 0x01
    ora.b _attribute
    sta.l 0x7E0001, x
    rep #0x20
    inc.b 0x00
    sep #0x20
    bra _step
_blank:
    sta.l 0x7E0000, x
    sta.l 0x7E0001, x
_step:
    inx
    inx
    dec.b 0x03
    bne _cell
    rts
}

.alloc vwf8_upload in code_c0 {
    .a8
    .i16
vwf8_open:
"""A menu opens: nothing queued, and the next allocation scans the maps (SRAM is not cleared at power on)."""
    lda.b #0
    sta.l vwf8.queued
    lda.l vwf8.frame
    inc
    sta.l vwf8.frame
    rtl

vwf8_drain:
"""The queued streams into VRAM (S-DD1 DMA, channel 0), in the frame's upload."""
    lda.l vwf8.frame
    inc
    sta.l vwf8.frame
    lda.l vwf8.queued
    beq _done
    ldx.w #0
_slot:
    pha
    lda.b #0x01
    sta.l 0x004800
    lda.b #0x09
    sta.l 0x004300
    lda.b #0x18
    sta.l 0x004301
    lda.l vwf8.queue, x
    sta.l 0x004302
    lda.l vwf8.queue + 1, x
    sta.l 0x004303
    lda.l vwf8.queue + 2, x
    sta.l 0x004304
    lda.l vwf8.queue + 3, x
    sta.l 0x004305
    lda.b #0
    sta.l 0x004306
    lda.l vwf8.queue + 4, x
    sta.l 0x002116
    lda.l vwf8.queue + 5, x
    sta.l 0x002117
    lda.b #0x01
    sta.l 0x004801
    sta.l 0x00420B
    lda.b #0
    sta.l 0x004800
    rep #0x20
    txa
    clc
    adc.w #_SLOT
    tax
    sep #0x20
    pla
    dec
    bne _slot
    sta.l vwf8.queued
_done:
    rtl
}
