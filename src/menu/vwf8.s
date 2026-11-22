"""
8x8 VWF for the menus' labels8 and names8 strings. tools/vwf8.py bakes each string as proportional tiles (one S-DD1
stream) and a record of the tile each cell shows; `vwf8_keys` sorts the records by the string's address. The 8x8
writer (`CA:BCAD`: $20-$22 = the string, $24 = tilemap shadow address, $26 = attribute, $27 = cells left, 0 = no
limit) goes through `vwf8_string` first: a string with a record is drawn from pool tiles, anything else by the game.

Pool: tiles 0D9-113 (free in every menu) and 300-3EF (above the 16x16 text) of the menus' BG1-3 CHR ($2000), one
index space. A string's tiles stay where they were uploaded and are reused while their owner marks are its own
(`home` per record), so a redraw costs no upload. Allocation is next-fit over the `used` marks; when nothing fits, the
three tilemap shadows ($7E:3100/3900/4100) are scanned once per frame for the tiles still shown. Uploads queue in
a ring drained after the game's own (`CA:6CD1`), BUDGET bytes per frame.

In battle (src/battle/vwf8.s) the same records draw into BG3 (CHR $4000): pool tiles 0D9-113 as in the menus and
13C-1FF in place of 300-3EF, the pool's tail past them never taken. `vwf8.battle` picks the battle tiles, the two
battle shadows ($7E:5100 / $5900, written together) and the battle drain (`vwf8_drain_battle`, in the line-216 IRQ).

The Talents combo slots print their special moves' battle16 names with the 16x16 VWF over two rows (`CA:5A95`);
`vwf8_combos` has those names baked for the 8x8 VWF instead, the long ones wrapped onto the slot's second row.
"""

.import "core/preamble"
.import "menu/text16"
.import "menu/pen8"

.include "vwf8.i"

_LOW_FIRST := 0x0D9
_LOW_TILES := 0x113 - _LOW_FIRST + 1
_HIGH_FIRST := 0x300
_POOL_TILES := _LOW_TILES + 0x3EF - _HIGH_FIRST + 1
_QUEUE_SLOTS := 64  ; a power of 2
_SLOT := 8  ; stream (3), bytes (2), VRAM word (2), 1: raw tiles (pen8)
_BUDGET := 0x0800
_SHADOWS := 0x7E3100  ; three 0x800-byte maps
_SHADOW_BYTES := 0x1800
_CHR := 0x2000
_BATTLE_HIGH_FIRST := 0x13C
_BATTLE_POOL_TILES := _LOW_TILES + 0x1FF - _BATTLE_HIGH_FIRST + 1
_BATTLE_SHADOWS := 0x7E5100  ; two 0x800-byte maps, the same tiles
_BATTLE_SHADOW_BYTES := 0x1000
_BATTLE_SECOND := 0x0800  ; the second shadow, from the first
_BATTLE_CHR := 0x4000
_BATTLE_LAST_LINE := 250  ; the drain stops past it: the line-258 IRQ (audio) waits for this one
_BLANK := 0xBF  ; the font's space
_NEWLINE := 0xFE
_END := 0xFF
_ROW := 0x40
_COMBO_CELLS := 12  ; a combo slot's row, up to the window's border

_record = 0x00  ; long pointer, saved and restored
_count = 0x04
_string = 0x20
_bank = 0x22
_cursor = 0x24
_attribute = 0x26
_cells = 0x27

.struct Vwf8 {
    byte queued
    byte head
    byte frame  ; counts drains
    byte scanned  ; frame of the last scan
    byte stale  ; 1: scan before the next allocation
    byte battle  ; 1: the battle pool, shadows and CHR
    word cursor  ; next-fit start
    word low  ; binary search
    word high
    word middle
    word id  ; the record's position in vwf8_keys
    word first  ; its first pool index
    word tile  ; its first tile number
    word budget
    byte[_QUEUE_SLOTS * _SLOT] queue
    byte[_POOL_TILES] used  ; 1: shown, or taken since the last scan
    word[_POOL_TILES] owner  ; id + 1 of the record whose tiles these are
    word[VWF8_RECORDS + PEN8_SLOTS] home  ; first pool index + 1, 0: not uploaded; past the baked: pen8's slots
}

.reserve vwf8 as Vwf8 in sram

; The 8x8 writer: `ldy #0 / ldx $24`.
.alloc at 0xCABCAD size 5 {
    jsr.w vwf8_cave_string
    nop
    nop
}

; The frame's upload, after the game's $7F slot: `lda #0x20 / trb 0601`.
.alloc at 0xCA6CD1 size 5 {
    jsr.w vwf8_cave_drain
    nop
    nop
}

; The two menu font loads (`ldx #0xA078`, the stream's address): a menu opens, the cache starts over.
.alloc at 0xCA64CD size 3 {
    jsr.w vwf8_cave_open
}
.alloc at 0xCA6832 size 3 {
    jsr.w vwf8_cave_open
}

; Talents combo slot: `jsr BAFD` (A = special move id, X = shadow address, M16 X16: the battle16 printer).
.alloc at 0xCA5A95 size 3 {
    jsr.w vwf8_cave_combo
}

.alloc vwf8_combo_cave at 0xCAFFAE size 5 {
vwf8_cave_combo:
    jsl vwf8_combo
    rts
}

.alloc vwf8_caves at 0xCAFF8C size 0x22 {
vwf8_cave_open:
    jsl vwf8_open
    ldx.w #0xA078
    rts

vwf8_cave_string:
    jsl vwf8_string
    bcc _game
    pla  ; the writer's return
    pla
    rts
_game:
    ldy.w #0
    ldx.b _cursor
    rts

vwf8_cave_drain:
    jsl vwf8_drain
    lda.b #0x20
    trb 0x0601
    rts
}

.alloc vwf8_code in text16 {
    .a8
    .i16
vwf8_string:
"""The string at $20 into the shadow at $24 from its tiles: carry set when drawn, X and Y as the writer leaves them."""
    rep #0x20
    lda.b _record
    pha
    lda.b _record + 2
    pha
    lda.b _count
    pha
    sep #0x20
    jsr.w _draw
    rep #0x20
    pla
    sta.b _count
    pla
    sta.b _record + 2
    pla
    sta.b _record
    sep #0x20
    rtl

vwf8_record:
"""vwf8_string for the record at $20-$22 whose position is vwf8.id."""
    rep #0x20
    lda.b _record
    pha
    lda.b _record + 2
    pha
    lda.b _count
    pha
    lda.b _string
    sta.b _record
    lda.b _string + 2
    sta.b _record + 2
    sep #0x20
    jsr.w _found
    rep #0x20
    pla
    sta.b _count
    pla
    sta.b _record + 2
    pla
    sta.b _record
    sep #0x20
    rtl

vwf8_combo:
"""
A = special move id, X = shadow address (M16 X16): its name over the slot's two rows from the 8x8 VWF, else the
battle16 printer's.
"""
    php
    rep #0x30
    pha
    phx
    pei (_string)
    pei (_bank)
    pei (_cursor)
    pei (_attribute)
    sec
    sbc.w #VWF8_COMBO_FIRST
    cmp.w #VWF8_COMBOS
    bcs _combo_printer
    pha
    asl
    asl
    tax
    lda.l vwf8_combos, x
    sta.b _string
    lda.l vwf8_combos + 2, x
    sta.b _bank
    pla
    clc
    adc.w #VWF8_KEYS
    sta.l vwf8.id
    lda.b _string
    ora.b _bank
    beq _combo_printer
    lda 9, s  ; the shadow address
    sta.b _cursor
    tax
    ldy.w #_COMBO_CELLS
    lda.w #0
_combo_clear:
    sta 0x7E0000, x
    sta.l 0x7E0000 + _ROW, x
    inx
    inx
    dey
    bne _combo_clear
    sep #0x20
    lda 0x06E6
    asl
    asl
    sta.b _attribute
    stz.b _cells
    jsl vwf8_record
    rep #0x30
    bcc _combo_printer
    pla
    sta.b _attribute
    pla
    sta.b _cursor
    pla
    sta.b _bank
    pla
    sta.b _string
    plx
    pla
    plp
    rtl
_combo_printer:
    rep #0x30
    pla
    sta.b _attribute
    pla
    sta.b _cursor
    pla
    sta.b _bank
    pla
    sta.b _string
    plx
    pla
    plp
    jml 0xC6F5FA

_draw:
    jsr.w _find
    bcc _refuse
_found:
    rep #0x20
    ldy.w #3
    lda.b [_record], y
    and.w #0x00FF
    sta.b _count
    sep #0x20
    beq _fill
    jsr.w _resident
    bcs _place
    lda.l vwf8.queued
    cmp.b #_QUEUE_SLOTS
    bcs _refuse
    jsr.w _allocate
    bcc _refuse
    jsr.w _enqueue
_place:
    jsr.w _tile_of
_fill:
    jsr.w _cells_out
    sec
    rts
_refuse:
    clc
    rts

_find:
"""Binary search of vwf8_keys for $20-$22: carry set, $00 = the record, vwf8.id = its position."""
    rep #0x30
    lda.w #0
    sta.l vwf8.low
    lda.w #VWF8_KEYS
    sta.l vwf8.high
_probe:
    lda.l vwf8.low
    cmp.l vwf8.high
    bcs _absent
    adc.l vwf8.high
    lsr
    sta.l vwf8.middle
    asl
    asl
    asl
    tax
    lda.l vwf8_keys + 2, x
    and.w #0x00FF
    sta.b _count
    lda.b _bank
    and.w #0x00FF
    cmp.b _count
    bne _ordered
    lda.b _string
    cmp.l vwf8_keys, x
    beq _hit
_ordered:
    bcc _below  ; the string sorts before the key
    lda.l vwf8.middle
    inc
    sta.l vwf8.low
    bra _probe
_below:
    lda.l vwf8.middle
    sta.l vwf8.high
    bra _probe
_hit:
    lda.l vwf8_keys + 4, x
    sta.b _record
    lda.l vwf8_keys + 6, x
    sta.b _record + 2
    lda.l vwf8.middle
    sta.l vwf8.id
    sep #0x20
    sec
    rts
_absent:
    sep #0x20
    .if VWF8_PEN {
        jsl pen8_find
        bcc _unknown
        rep #0x20
        lda.l pen8.slot
        and.w #0x00FF
        clc
        adc.w #VWF8_RECORDS
        sta.l vwf8.id
        sep #0x20
        lda.l pen8.fresh
        beq _drawn
        rep #0x20
        lda.l vwf8.id
        asl
        tax
        lda.w #0
        sta.l vwf8.home, x  ; new tiles in the slot: upload them
        sep #0x20
_drawn:
        sec
        rts
_unknown:
    }
    clc
    rts

_resident:
"""Carry set when the record's tiles are still the ones it uploaded (vwf8.first), marked used again."""
    rep #0x20
    lda.l vwf8.id
    asl
    tax
    lda.l vwf8.home, x
    beq _stale
    dec
    sta.l vwf8.first
    asl
    tax
    lda.l vwf8.id
    inc
    ldy.b _count
_own:
    cmp.l vwf8.owner, x
    bne _stale
    inx
    inx
    dey
    bne _own
    lda.l vwf8.first
    tax
    ldy.b _count
    sep #0x20
    lda.b #1
_mark:
    sta.l vwf8.used, x
    inx
    dey
    bne _mark
    sec
    rts
_stale:
    sep #0x20
    clc
    rts

_allocate:
"""_count free pool tiles in a row: vwf8.first, owned and marked; carry clear when the pool is full."""
    lda.l vwf8.stale
    beq _fit
    lda.b #0
    sta.l vwf8.stale
    jsr.w _rescan
_fit:
    rep #0x20
    lda.l vwf8.cursor
    tax
    sep #0x20
    jsr.w _fit_from
    bcs _take
    ldx.w #0
    jsr.w _fit_from
    bcs _take
    lda.l vwf8.frame
    cmp.l vwf8.scanned
    beq _full
    jsr.w _rescan
    ldx.w #0
    jsr.w _fit_from
    bcs _take
_full:
    clc
    rts
_take:
    rep #0x20
    txa
    sec
    sbc.b _count
    sta.l vwf8.first
    inc
    pha
    lda.l vwf8.id
    asl
    tax
    pla
    sta.l vwf8.home, x
    lda.l vwf8.first
    clc
    adc.b _count
    sta.l vwf8.cursor
    lda.l vwf8.first
    asl
    tax
    lda.l vwf8.id
    inc
    ldy.b _count
_owned:
    sta.l vwf8.owner, x
    inx
    inx
    dey
    bne _owned
    lda.l vwf8.first
    tax
    ldy.b _count
    sep #0x20
    lda.b #1
_taken:
    sta.l vwf8.used, x
    inx
    dey
    bne _taken
    sec
    rts

_fit_from:
"""From pool index X, the end of _count free tiles in a row inside one range: carry set, X past them."""
    ldy.w #0
_try:
    cpx.w #_POOL_TILES
    bcs _none
    cpx.w #_LOW_TILES
    bne _same_range
    ldy.w #0
_same_range:
    lda.l vwf8.used, x
    bne _busy
    inx
    iny
    cpy.b _count
    bne _try
    sec
    rts
_busy:
    ldy.w #0
    inx
    bra _try
_none:
    clc
    rts

_rescan:
"""vwf8.used from the shadows: the pool tiles a map shows."""
    lda.l vwf8.frame
    sta.l vwf8.scanned
    ldx.w #_POOL_TILES - 1
    lda.b #0
_clear:
    sta.l vwf8.used, x
    dex
    bpl _clear
    lda.l vwf8.battle
    beq _menu_scan
    jmp.w _battle_rescan
_menu_scan:
    rep #0x20
    ldx.w #0
_entry:
    lda.l _SHADOWS, x
    and.w #0x03FF
    cmp.w #_HIGH_FIRST
    bcs _high
    sbc.w #_LOW_FIRST - 1  ; carry clear: - _LOW_FIRST
    cmp.w #_LOW_TILES
    bcs _next
    bra _shown
_high:
    sbc.w #_HIGH_FIRST - _LOW_TILES
    cmp.w #_POOL_TILES
    bcs _next
_shown:
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

_battle_rescan:
"""_rescan's battle half: the two battle shadows, then the pool's tail past the battle tiles taken for good."""
    rep #0x20
    ldx.w #0
_battle_entry:
    lda.l _BATTLE_SHADOWS, x
    and.w #0x03FF
    cmp.w #_BATTLE_HIGH_FIRST
    bcs _battle_high
    sbc.w #_LOW_FIRST - 1  ; carry clear: - _LOW_FIRST
    cmp.w #_LOW_TILES
    bcs _battle_next
    bra _battle_shown
_battle_high:
    sbc.w #_BATTLE_HIGH_FIRST - _LOW_TILES
    cmp.w #_BATTLE_POOL_TILES
    bcs _battle_next
_battle_shown:
    phx
    tax
    sep #0x20
    lda.b #1
    sta.l vwf8.used, x
    rep #0x20
    plx
_battle_next:
    inx
    inx
    cpx.w #_BATTLE_SHADOW_BYTES
    bcc _battle_entry
    sep #0x20
    ldx.w #_BATTLE_POOL_TILES
    lda.b #1
_tail:
    sta.l vwf8.used, x
    inx
    cpx.w #_POOL_TILES
    bcc _tail
    rts

_tile_of:
"""vwf8.tile: the tile number of pool index vwf8.first."""
    rep #0x20
    lda.l vwf8.first
    cmp.w #_LOW_TILES
    bcs _upper
    adc.w #_LOW_FIRST
    bra _tile
_upper:
    tax
    lda.l vwf8.battle
    and.w #0x00FF
    beq _menu_upper
    txa
    sec
    adc.w #_BATTLE_HIGH_FIRST - _LOW_TILES - 1
    bra _tile
_menu_upper:
    txa
    sec
    adc.w #_HIGH_FIRST - _LOW_TILES - 1
_tile:
    sta.l vwf8.tile
    sep #0x20
    rts

_enqueue:
"""The record's stream into the ring, for its tiles' CHR. IRQs off: the battle drain runs in one."""
    php
    sei
    jsr.w _tile_of
    lda.l vwf8.head
    clc
    adc.l vwf8.queued
    and.b #_QUEUE_SLOTS - 1
    rep #0x20
    and.w #0x00FF
    asl
    asl
    asl
    tax
    lda.b [_record]
    sta.l vwf8.queue, x
    ldy.w #1
    lda.b [_record], y
    sta.l vwf8.queue + 1, x
    lda.b _count
    asl
    asl
    asl
    asl
    sta.l vwf8.queue + 3, x
    lda.l vwf8.battle
    and.w #0x00FF
    beq _menu_chr
    lda.w #_BATTLE_CHR
    bra _chr
_menu_chr:
    lda.w #_CHR
_chr:
    sta.l vwf8.middle  ; scratch
    lda.l vwf8.tile
    asl
    asl
    asl
    clc
    adc.l vwf8.middle
    sta.l vwf8.queue + 5, x
    lda.l vwf8.id
    cmp.w #VWF8_RECORDS
    sep #0x20
    lda.b #0
    rol
    sta.l vwf8.queue + 7, x
    lda.l vwf8.queued
    inc
    sta.l vwf8.queued
    plp
    rts

_cells_out:
"""The record's cells into the shadow from $24, as the writer would (newlines, the $27 limit)."""
    ldx.b _cursor
    ldy.w #4
_cell:
    lda.b [_record], y
    cmp.b #_END
    beq _done
    cmp.b #_NEWLINE
    bne _glyph
    rep #0x20
    lda.b _cursor
    clc
    adc.w #_ROW
    sta.b _cursor
    tax
    sep #0x20
    iny
    bra _cell
_glyph:
    cmp.b #0
    bne _tiled
    lda.b #_BLANK
    sta 0x7E0000, x
    lda.b _attribute
    bra _attribute_out
_tiled:
    rep #0x20
    and.w #0x00FF
    clc
    adc.l vwf8.tile
    dec
    sep #0x20
    sta 0x7E0000, x
    xba
    ora.b _attribute
_attribute_out:
    sta 0x7E0001, x
    lda.l vwf8.battle
    beq _one_shadow
    rep #0x20
    lda 0x7E0000, x
    sta.l 0x7E0000 + _BATTLE_SECOND, x
    sep #0x20
_one_shadow:
    inx
    inx
    iny
    lda.b _cells
    beq _cell
    dec
    sta.b _cells
    bne _cell
_done:
    rep #0x20
    tya
    sec
    sbc.w #4
    tay
    sep #0x20
    rts

vwf8_open:
"""A menu opens: nothing uploaded is trusted, nothing queued, the next allocation scans the maps."""
    lda.b #0
    bra _open

vwf8_battle_ready:
"""vwf8_battle_open unless the battle pool is open (a savestate taken mid-fight never ran the fight's start)."""
    lda.l vwf8.battle
    cmp.b #1
    bne vwf8_battle_open
    rtl

vwf8_battle_open:
"""vwf8_open for a battle: the battle pool from here on (8-bit A)."""
    lda.b #1
_open:
    sta.l vwf8.battle
    lda.b #0
    sta.l vwf8.queued
    sta.l vwf8.head
    lda.b #1
    sta.l vwf8.stale
    rep #0x20
    lda.w #0
    sta.l vwf8.cursor
    ldx.w #2 * ( VWF8_RECORDS + PEN8_SLOTS ) - 2
_forget:
    sta.l vwf8.home, x
    dex
    dex
    bpl _forget
    sep #0x20
    rtl
}

.macro vwf8_send(channel, mask) {
    """
    Queue slot X's tiles into VRAM through DMA `channel` (`mask` its bit): an S-DD1 stream, or pen8's tiles as they
    are. M8 X16; A clobbered.
    """
    lda.l vwf8.queue + 7, x
    eor.b #1
    asl
    asl
    asl
    ora.b #0x01  ; 0x09 through the S-DD1, 0x01 raw
    sta.l 0x004300 + channel
    lda.b #0x18
    sta.l 0x004301 + channel
    rep #0x20
    lda.l vwf8.queue, x
    sta.l 0x004302 + channel
    lda.l vwf8.queue + 2, x  ; bank, then the size's low byte
    sta.l 0x004304 + channel
    lda.l vwf8.queue + 3, x
    sta.l 0x004305 + channel
    lda.l vwf8.queue + 5, x
    sta.l 0x002116
    sep #0x20
    lda.l vwf8.queue + 7, x
    dec
    and.b #mask  ; the S-DD1 decompresses the stream, not the raw tiles
    sta.l 0x004800
    sta.l 0x004801
    lda.b #mask
    sta.l 0x00420B
    lda.b #0
    sta.l 0x004800
}

.alloc vwf8_upload in code_c9 {
    .a8
    .i16
vwf8_drain:
"""Queued streams into VRAM (S-DD1 DMA, channel 0) until BUDGET bytes, in the frame's upload."""
    jsr.w _begin
_slot:
    jsr.w _next
    bcc _done
    vwf8_send(0x00, 0x01)
    bra _slot
_done:
    rtl

vwf8_drain_battle:
"""
The battle's: in the line-216 IRQ's DMA list (M8 X16, DB 0), channel 1 as the list's own jobs (channel 0 may be
half set up by the cel streamer), the E / F windows on pages 2 / 3 (text16) and back, until BATTLE_LAST_LINE. What
is left asks the list for the next frame (its BG3 map job). Then the list's wait for V-blank, which this replaces.
"""
    lda.l vwf8.battle
    cmp.b #1
    bne _no_drain
    lda.l vwf8.queued
    beq _no_drain
    cmp.b #_QUEUE_SLOTS + 1
    bcc _battle_drain
    lda.b #0  ; SRAM left by another build or a cold boot: nothing in it was queued here
    sta.l vwf8.queued
_no_drain:
    jmp.w _vblank
_battle_drain:
    lda.l 0x004800
    pha
    lda.l 0x004806
    pha
    lda.l 0x004807
    pha
    lda.b #2
    sta.l 0x004806
    lda.b #3
    sta.l 0x004807
    jsr.w _begin
_battle_slot:
    jsr.w _line
    cmp.w #_BATTLE_LAST_LINE
    sep #0x20
    bcs _battle_done
    jsr.w _next
    bcc _battle_done
    rep #0x20
    lda.l vwf8.queue + 5, x
    cmp.w #_BATTLE_CHR
    bcc _not_ours
    cmp.w #_BATTLE_CHR + 0x1000
    bcs _not_ours
    sep #0x20
    vwf8_send(0x10, 0x02)
    bra _battle_slot
_not_ours:
    sep #0x20  ; a slot outside the battle pool's CHR: the ring is not ours, drop it
    lda.b #0
    sta.l vwf8.queued
_battle_done:
    pla
    sta.l 0x004807
    pla
    sta.l 0x004806
    pla
    sta.l 0x004800
    lda.b #0x01  ; channel 1 as the list leaves it
    sta.l 0x004310
    lda.l vwf8.queued
    beq _vblank
    lda.b #0x04
    tsb.w 0x094A
_vblank:
    lda.l 0x004212
    bpl _vblank
    rtl

_line:
"""A (16-bit on return) = the scanline now."""
    lda.b #0xFF
    sta.l 0x004201
    lda.l 0x002137
    lda.l 0x00213F
    lda.l 0x00213D
    xba
    lda.l 0x00213D
    and.b #0x01
    xba
    rep #0x20
    rts

_begin:
    lda.l vwf8.frame
    inc
    sta.l vwf8.frame
    rep #0x20
    lda.w #0
    sta.l vwf8.budget
    sep #0x20
    rts

_next:
"""The ring's head slot: carry set, X its offset, popped and counted; carry clear when empty or BUDGET spent."""
    rep #0x20
    lda.l vwf8.budget
    cmp.w #_BUDGET
    sep #0x20
    bcs _empty
    lda.l vwf8.queued
    beq _empty
    dec
    sta.l vwf8.queued
    lda.l vwf8.head
    rep #0x20
    and.w #0x00FF
    asl
    asl
    asl
    tax
    lda.l vwf8.budget
    clc
    adc.l vwf8.queue + 3, x
    sta.l vwf8.budget
    sep #0x20
    lda.l vwf8.head
    inc
    and.b #_QUEUE_SLOTS - 1
    sta.l vwf8.head
    sec
    rts
_empty:
    clc
    rts
}
