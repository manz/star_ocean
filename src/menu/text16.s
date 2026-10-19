"""
16x16 strings (battle16, menu16), one byte per character in the text16 pool (build/gen/text16.i,
tools/encode_menus.py): the id lists stay where the game searches them, the position found picks a 24-bit pointer
instead of an offset. Where the game copies a string into a u16 buffer the bytes are widened back.
"""

.import "core/preamble"

.include "text16.i"

END := 0xFF

.macro pointer_at(table) {
    """X = 2 * id-list position (M16 X16) -> $28-$2A = the string."""
    phx
    txa
    lsr
    clc
    adc 1, s  ; 3 * position
    tax
    lda.l table, x
    sta.b 0x28
    lda.l table + 1, x
    sta.b 0x29
    plx
}

.alloc battle16_pointer in code_c8 {
    pointer_at(battle16_pointers)
    rtl
}

.alloc menu16_pointer in code_c8 {
    pointer_at(menu16_pointers)
    rtl
}

; CA:B2B0 (item panel template, id -> $28): `lda D7:254B,x / clc / adc #2FD1 / sta 28` for battle16,
; `lda 7F:2800,x / clc / adc #3000 / sta 28` for menu16.
.alloc at 0xCAB2D9 size 10 {
    jsl battle16_pointer
    .db 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA
}
.alloc at 0xCAB307 size 10 {
    jsl menu16_pointer
    .db 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA
}

; CA:B361: append the string at [$28] to the u16 buffer at [$2C].
.alloc at 0xCAB361 size 9 {
    php
    rep #0x20
    jsl append_wide
    plp
    rts
}

.alloc append_wide in code_c8 {
"""[$28] = one byte per code, END-terminated -> u16 codes at [$2C], $2C left after them (M16)."""
    ldy.w #0
_next:
    lda [0x28], y
    and.w #0x00FF
    cmp.w #END
    beq _done
    sta [0x2C]
    inc.b 0x2C
    inc.b 0x2C
    iny
    bra _next
_done:
    rtl
}

; CA:B313 (8x8 name -> u16 through C0:4B60): codes 03 and 0B were Japanese symbols with their own glyphs, French
; uses them as letters: `beq` to the next instruction.
.alloc at 0xCAB32B size 2 {
    .db 0xF0, 0x00
}
.alloc at 0xCAB330 size 2 {
    .db 0xF0, 0x00
}

; CA:B382 laid the text over the Japanese template (20 cells a line, wrapping mid-word): copy it as it is, the
; VWF wraps at spaces.
.alloc at 0xCAB382 size 24 {
    php
    rep #0x20
_next:
    lda [0x28]
    sta [0x2C]
    inc.b 0x28
    inc.b 0x28
    inc.b 0x2C
    inc.b 0x2C
    cmp.w #0xFFFF
    bne _next
    sep #0x20
    plp
    rts
}

; CA:B1F4 (template: pad with spaces up to a column): the columns were 12 px cells, proportional text would land
; anywhere; one space instead.
.alloc at 0xCAB1F4 size 14 {
    rep #0x20
    lda.w #0x0010
    sta [0x2C]
    inc.b 0x2C
    inc.b 0x2C
    sep #0x20
    rts
}

; CA:AC96 (menu16 id in Y -> its text laid over the template at $7E:C1B3 + X, e.g. formation descriptions):
; `sep #20 / lda #7F / pha / plb / jsr ACA9 (find) / jsr ACCC (merge from $7F:3000)`.
.alloc at 0xCAACA0 size 6 {
    jsl menu16_copy
    nop
    nop
}

.alloc menu16_copy in code_c8 {
"""$20 = menu16 id, X = offset in $7E:C1B3: the string widened there, FFFF after it (the VWF wraps it)."""
    php
    rep #0x30
    phb
    phx
    ldx.w #0
_find:
    lda.l 0x7F2000, x
    beq _missing
    cmp.b 0x20
    beq _found
    inx
    inx
    bra _find
_missing:
    ldx.w #0
_found:
    txa
    lsr
    sta.b 0x20
    txa
    clc
    adc.b 0x20
    tax  ; 3 * position
    sep #0x20
    lda.l menu16_pointers + 2, x
    pha
    plb
    rep #0x20
    lda.l menu16_pointers, x
    tay
    plx
_next:
    lda.w 0x0000, y
    and.w #0x00FF
    cmp.w #END
    beq _end
    sta.l 0x7EC1B3, x
    inx
    inx
    iny
    bra _next
_end:
    lda.w #0xFFFF
    sta.l 0x7EC1B3, x
    plb
    plp
    rtl
}
