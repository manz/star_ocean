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
    lda 0x7F2000, x
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
    sta 0x7EC1B3, x
    inx
    inx
    iny
    bra _next
_end:
    lda.w #0xFFFF
    sta 0x7EC1B3, x
    plb
    plp
    rtl
}

; The battle copy of the 16x16 append (bank C0) still read the Japanese words at D7:254B / D7:2FD1, which the
; pool reclaimed: past the end the renderer's WRAM pointer walks into direct page and the APU handshake hangs.
; (C0:460A, the battle16 printer, goes through src/menu/vwf16.s.)

.alloc battle16_locate in code_c8 {
"""Y = 2 * id-list position (M16 X16) -> DB:Y = the string; X kept."""
    phx
    phy
    tya
    lsr
    clc
    adc 1, s  ; 3 * position
    tax
    ply
    sep #0x20
    lda.l battle16_pointers + 2, x
    pha
    plb
    rep #0x20
    lda.l battle16_pointers, x
    tay
    plx
    rtl
}

; C0:423E (battle16 id -> u16 codes at [$BE], $BE left on the FFFF), from the search hit: `lda 254B,y / tay`, then
; the copy loop.
.alloc at 0xC04261 size 4 {
    jml battle16_append
}

.alloc battle16_append in code_c8 {
"""Y = 2 * id-list position: the string widened at [$BE], FFFF after it, then C0:4279 (ply / plb / plp / rtl)."""
    jsl battle16_locate
_next:
    lda.w 0x0000, y
    and.w #0x00FF
    cmp.w #END
    beq _end
    sta [0xBE]
    inc.b 0xBE
    inc.b 0xBE
    iny
    bra _next
_end:
    lda.w #0xFFFF
    sta [0xBE]
    jml 0xC04279
}

; C0:4B13 (battle16 id in $20 -> X = its Japanese string in bank D7) has no caller: nothing jumps or points to it
; and play never runs it. A found id now traps instead of handing out reclaimed bytes, so a caller shows up in a
; hunt (betaplayer-so-hunt stops on BRK).
.alloc at 0xC04B30 size 2 {
    brk #0x4B
}

.macro op(kind, word) {
    """One template op: kind (low nibble) and the value its high nibble adds to `word`."""
    .db kind
    .dw word
}

; CA:B0EB builds the item / talent notices into the u16 buffer from templates of 3-byte ops, an offset from C6:F523
; each: 01 end, 03 a code, 05 pad, 06 / 16 item name, 07 / 17 / 97 menu16 string, 82 character name. The Japanese
; chained particles (は, を, 「, 」...) as menu16 strings: the French templates put the words in French order.
.alloc at 0xC6F523 size 0xD7 {
_table:
    .dw _rows - _table, _got - _table, _equip - _table, _equip_more - _table
    .for n := 0, 4 {
        .dw _level - _table
    }
    .dw _learnt - _table, _raised - _table, _made - _table, _identified - _table
    .for n := 0, 4 {
        .dw _secret - _table
    }
    .for n := 0, 4 {
        .dw 0x00D7  ; past the templates, as in the Japanese
    }
_rows:
    op(0x03, 0x000D)
    op(0x03, 0x000D)
    .db 0x01
; Obtenu : <item> !
_got:
    op(0x07, 0xFB9C)
    op(0x06, 0x1387)
    op(0x07, 0xFB9A)
    .db 0x01
_equip:
    op(0x16, 0x1387)
    op(0x05, 0x0009)
    op(0x27, 0xF1CC)
    op(0x03, 0x000D)
    op(0x17, 0xFDE8)
    .db 0x01
_equip_more:
    op(0x16, 0x1387)
    op(0x05, 0x0009)
    op(0x27, 0xF1CC)
    op(0x03, 0x000D)
    op(0x32, 0x0000)
    op(0x17, 0xFDE8)
    .db 0x01
_level:
    op(0x17, 0x0000)
    .db 0x01
; <name> apprend le talent "<talent>" !
_learnt:
    op(0x82, 0x0000)
    op(0x07, 0xFB90)
    op(0x97, 0xFC6C)
    op(0x07, 0xFB91)
    .db 0x01
; Le talent "<talent>" de <name> / passe au niveau <n> !
_raised:
    op(0x07, 0xFB92)
    op(0x97, 0xFC6C)
    op(0x07, 0xFB93)
    op(0x82, 0x0000)
    op(0x03, 0x000D)
    op(0x07, 0xFB94)
    op(0x17, 0xFBE0)
    op(0x07, 0xFB9A)
    .db 0x01
; Création réussie : <item> !
_made:
    op(0x07, 0xFB9D)
    op(0x16, 0x1387)
    op(0x07, 0xFB9A)
    .db 0x01
; Identifié : <item> !
_identified:
    op(0x07, 0xFB9E)
    op(0x16, 0x1387)
    op(0x07, 0xFB9A)
    .db 0x01
; <name> éveille un don inné secret : / "<don>" !
_secret:
    op(0x82, 0x0000)
    op(0x07, 0xFB9B)
    op(0x03, 0x000D)
    op(0x07, 0xFBC2)
    op(0x16, 0xF9C4)
    op(0x07, 0xFB91)
    .db 0x01
}
