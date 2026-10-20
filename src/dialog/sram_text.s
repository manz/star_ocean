"""
Scene text in cart SRAM.

The scene's text block unpacks to $70:0000 instead of $7E:B873 (7.5 KB of WRAM, too small for French), and the
message the engine selects is copied to $7E:B873. Every stream reader keeps its DB-relative `lda.w 0,x` on
that one message.
"""

.import "core/preamble"

TEXT_BUFFER := 0xB873  ; $7E:B873, the engine's script buffer

.reserve sram_text 0x5000 in sram  ; 20 KB: the largest French block is 13.1 KB
.reserve sram_text_size 2 in sram
.reserve text_saved_page 1 in sram  ; $4806 before the unpack switched it, 0 when it did not

PAGE_BANKS := 0x40  ; pseudo-banks $40-$5F: ROM pages 6-7 (a816.toml [map.1])
E_WINDOW := 0x004806  ; S-DD1 MMC: bank $E0-$EF page

; scene_load_script: `jsl unpack` with X = $B873 -> our SRAM unpack.
.alloc at 0xC61137 size 4 {
    jsl text_unpack_sram
}

.macro _select_message_hook() {
    """Over `lda $B873,x / clc / adc #$B873 / sta $03D5` (X = message * 2), 10 bytes."""
    jsl text_select_message
    sta 0x03D5
    nop
    nop
    nop
}

; The two message selects: the event op at C2:1C2E, and text_message_select.
.alloc at 0xC21C47 size 10 {
    _select_message_hook()
}

.alloc at 0xC21CAC size 10 {
    _select_message_hook()
}

.macro _lz_copy() {
    """Back-reference `b0 b1` at Y (carry clear): copy (b1 >> 4) + 3 bytes from X - (b0 | (b1 & 0x0F) << 8)."""
    phy
    lda [0xB6], y
    and #0xF0
    sta 0xA6  ; $A5-$A6 = (b1 & 0xF0) << 8, $A7 = 0
    rep #0x20
    txa
    adc 0xA5
    sec
    sbc [0xB1], y  ; X - distance
    txy
    tax
    lda 0xA6
    lsr
    lsr
    lsr
    lsr
    adc.w #2  ; length - 1
    mvn 0x70, 0x70
    sep #0x20
    tyx
    ply
    iny
    iny
}

.alloc text_unpack_sram in code_c0 {
"""
`unpack` (C0:4C53) into sram_text. In: A = source bank, Y = container address (M8 X16, D = 0).

    Container: kind (0x81 LZSS, 0x83 LZSS + RLE, else raw), packed size at +1, raw size - 1 at +5, data at +9.
    The game's own loop: flag bits shift out of $A4 with a marker bit behind them, one end check per item, DB on
    the destination. Scratch: the direct-page bytes `unpack` itself uses.
"""
    php
    phb
    sep #0x20
    rep #0x10
    jsr _map_page
    sta 0xB3
    sta 0xB8
    stz 0xB1
    stz 0xB2
    stz 0xB7
    stz 0xA5
    stz 0xA7
    stz 0xAB
    pha
    lda #0x70
    pha
    plb
    pla
    ldx.w #sram_text & 0xFFFF
    lda [0xB1], y
    cmp #0x81
    beq _lzss
    cmp #0x83
    beq _rle
    jmp _raw
_lzss:
    jsr _lz_setup
    sec
    bra _lzss_flags
_lzss_next:
    ror 0xA4
    bne _lzss_item
_lzss_flags:
    lda [0xB1], y
    ror
    sta 0xA4
    iny
_lzss_item:
    bcc _lzss_reference
    lda [0xB1], y
    sta.w 0, x
    iny
    inx
    cpy 0xA2
    bcc _lzss_next
    jmp _done
_lzss_reference:
    _lz_copy()
    cpy 0xA2
    bcc _lzss_next
    jmp _done
_rle:
    jsr _lz_setup
    sec
    bra _rle_flags
_rle_next:
    ror 0xA4
    bne _rle_item
_rle_flags:
    lda [0xB1], y
    ror
    sta 0xA4
    iny
_rle_item:
    bcc _rle_reference
    lda [0xB1], y
    sta.w 0, x
    iny
    inx
    cpy 0xA2
    bcc _rle_next
    jmp _done
_rle_reference:
    lda [0xB6], y
    cmp #0xF0
    bcs _run
    _lz_copy()
    cpy 0xA2
    bcc _rle_next
    jmp _done
_run:
    and #0x0F
    beq _long_run
    clc
    adc #3
    sta 0xAA  ; run length, $AB = 0
    lda [0xB1], y
    iny
    iny
    bra _fill
_long_run:
    lda [0xB1], y
    clc
    adc #0x13
    sta 0xAA
    lda #0
    rol
    sta 0xAB
    iny
    iny
    lda [0xB1], y
    iny
_fill:
    sta.w 0, x
    inx
    rep #0x20
    dec 0xAA
    sep #0x20
    bne _fill
    stz 0xAB
    cpy 0xA2
    bcc _rle_next
    jmp _done
_raw:
    rep #0x20
    iny
    iny
    iny
    iny
    iny
    lda [0xB1], y
    clc
    adc.w #sram_text & 0xFFFF
    sta 0xAA  ; last byte's address
    iny
    iny
    iny
    iny
    sep #0x20
_raw_byte:
    lda [0xB1], y
    sta.w 0, x
    iny
    inx
    cpx 0xAA
    bcc _raw_byte
    beq _raw_byte
_done:
    rep #0x20
    txa
    sec
    sbc.w #sram_text & 0xFFFF
    sta.l sram_text_size
    sep #0x20
    lda.l text_saved_page
    beq _restored
    sta.l E_WINDOW
_restored:
    plb
    plp
    rtl

_map_page:
"""
A = source bank (M8). A pseudo-bank $40-$5F switches the E window to page 6 or 7 and returns its $E0-$EF
    bank; any other bank returns as is. text_saved_page keeps the page to restore (0: none).
"""
    pha
    lda #0
    sta.l text_saved_page
    pla
    cmp #PAGE_BANKS
    bcc _not_paged
    cmp #PAGE_BANKS + 0x20
    bcs _not_paged
    pha
    lda.l E_WINDOW
    sta.l text_saved_page
    lda 1, s
    lsr
    lsr
    lsr
    lsr
    clc
    adc #2  ; $4X -> 6, $5X -> 7
    sta.l E_WINDOW
    pla
    and #0x0F
    ora #0xE0
_not_paged:
    rts

_lz_setup:
"""Y = container -> Y = container + 1, $A2 = end of data, [$B1],y on the data and [$B6],y one byte on."""
    rep #0x20
    iny
    tya
    clc
    adc [0xB1], y
    sta 0xA2
    sep #0x20
    lda #8
    sta 0xB1
    inc
    sta 0xB6
    rts
}

.alloc text_select_message in code_c0 {
"""X = message * 2 (M16 X16, DB = $7E): message X/2 of sram_text -> $7E:B873. Out: A = $B873."""
    phx
    phy
    phb
    txa
    inc
    inc
    cmp.l sram_text  ; offset[0] = offset table size
    bcc _not_last
    lda.l sram_text_size
    bra _length
_not_last:
    lda.l sram_text + 2, x
_length:
    sec
    sbc.l sram_text, x
    dec
    pha
    lda.l sram_text, x
    clc
    adc.w #sram_text & 0xFFFF
    tax
    ldy.w #TEXT_BUFFER
    pla
    mvn 0x70, 0x7E
    plb
    ply
    plx
    lda.w #TEXT_BUFFER
    rtl
}
