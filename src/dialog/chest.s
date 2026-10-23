"""
Treasure chest message: `C2:05F2` builds it in $7E:6100 (colour, the item or the Fol amount, colour) and ended it
with the Japanese "を手に入れました。" written as immediates; the French suffix is copied there instead. The field
item find (syscall 55, `C6:DD40`) builds it the same way and gets the same suffix. The item list (`C6:DAD7`, the
non-zero words of $02EF) is built by `item_list_build` instead. Details: notes/dialog/item_messages.md.
`C2:5169` wrote a whole message as immediates ("持ち物がいっぱいです", the inventory is full).
"""

.import "core/preamble"
.include "item_list.i"

ITEM_NAMES := 0x1387  ; names8 id of item 0 (tools/item_list.py)

; C2:0669: X = where the suffix goes (DB = $7E, M16 X16), then `plx / rts`.
.alloc at 0xC20669 size 0x2C {
    txy
    ldx.w #chest_found & 0xFFFF
    lda.w #sizeof(chest_found) - 1
    mvn chest_found >> 16, 0x7E
    plx
    rts
}

; C6:DD76: X = where the suffix goes (DB = $7E, M16 X16); C6:DDA0 then does `sep / plb / rtl`.
.alloc at 0xC6DD76 size 0x2A {
    txy
    ldx.w #chest_found & 0xFFFF
    lda.w #sizeof(chest_found) - 1
    mvn chest_found >> 16, 0x7E
    bra _item_find_done
}

.label _item_find_done = 0xC6DDA0

; C6:DAD4: the item list (M16 X16, DB = $7E, after `rep #0x20`), up to its `plb / rts`. It joined the names with
; "、" and let the engine break the line, which in French cuts a name and draws a second break over the line before.
.alloc at 0xC6DAD4 size 0xCD {
    ldx.w #0x6100
    stx 0x03D5
    stz 0x0498
    jsl item_list_build
    plb
    rts
}

.alloc item_list_build in code_c6 {
"""
X = the message ($7E:6100): each non-zero word of $02EF as [color] 6, [item] id, [color] 2, joined by ", " while
    the next name fits the line, else by "," and a break: a new line, or a page once the window's 3 lines are
    used. Then the suffix: ' a été obtenu !' for one item, 'ont été obtenus !' on a line of its own for more.
    DP $00 slot, $02 items, $04 line width, $06 lines, $08 id, $0A width.
"""
    stz 0x00
    stz 0x02
    stz 0x04
    lda.w #1
    sta 0x06
_slot:
    ldy 0x00
    lda.w 0x02EF, y
    beq _next
    bpl _low
    and.w #0xFF
    ora.w #0x100
    bra _id
_low:
    and.w #0xFF
_id:
    sta 0x08
    phx
    tax
    lda.l item_widths, x
    and.w #0xFF
    sta 0x0A
    plx
    lda 0x02
    beq _place
    lda 0x04
    clc
    adc.w #ITEM_LIST_SEPARATOR
    adc 0x0A
    cmp.w #ITEM_LIST_WINDOW - ITEM_LIST_COMMA + 1  ; room left for the comma a later break adds
    bcs _wrap
    lda.w #0x055E  ; ", " (text/so_fr.tbl)
    sta.w 0x0000, x
    inx
    inx
    lda 0x04
    clc
    adc.w #ITEM_LIST_SEPARATOR
    sta 0x04
    bra _place
_wrap:
    sep #0x20
    lda.b #0x5E  ; ","
    sta.w 0x0000, x
    rep #0x20
    inx
    jsr _break
    stz 0x04
_place:
    lda.w #0x0604  ; [color] 6
    sta.w 0x0000, x
    lda.w #0x8086  ; [item]
    sta.w 0x0002, x
    lda 0x08
    clc
    adc.w #ITEM_NAMES
    sta.w 0x0004, x
    lda.w #0x0204  ; [color] 2
    sta.w 0x0006, x
    txa
    clc
    adc.w #8
    tax
    lda 0x04
    clc
    adc 0x0A
    sta 0x04
    inc 0x02
_next:
    inc 0x00
    inc 0x00
    lda 0x00
    cmp.w #8
    beq _suffix
    jmp _slot
_suffix:
    lda 0x02
    cmp.w #2
    bcs _plural
    txy
    ldx.w #chest_found & 0xFFFF
    lda.w #sizeof(chest_found) - 1
    mvn chest_found >> 16, 0x7E
    rtl
_plural:
    jsr _break
    txy
    ldx.w #items_found & 0xFFFF
    lda.w #sizeof(items_found) - 1
    mvn items_found >> 16, 0x7E
    rtl

_break:
    sep #0x20
    lda 0x06
    cmp.b #3
    bcs _page
    inc 0x06
    stz.w 0x0000, x  ; new line
    bra _broke
_page:
    lda.b #1
    sta 0x06
    sta.w 0x0000, x  ; page: wait, then a clear window
_broke:
    rep #0x20
    inx
    rts
}

.alloc item_widths in code_c4 {
    .incbin "item_widths.bin"
}

.alloc items_found in code_c6 {
"""'ont été obtenus !' (text/so_fr.tbl), then page wait and end."""
    .db 0x38, 0x37, 0x3D, 0x05, 0x48, 0x3D, 0x48, 0x05, 0x38, 0x2B, 0x3D, 0x2E, 0x37, 0x3E, 0x3C, 0x05, 0x5F
    .db 0x01, 0xFF, 0xFF
}

; C2:516F: X = $6100, the message (DB = $7E, M16 X16); C2:519F goes on with `sep #0x20`.
.alloc at 0xC2516F size 0x30 {
    phy
    txy
    ldx.w #inventory_full & 0xFFFF
    lda.w #sizeof(inventory_full) - 1
    mvn inventory_full >> 16, 0x7E
    ply
    bra _inventory_full_done
}

.label _inventory_full_done = 0xC2519F

.alloc inventory_full in code_c8 {
"""'Impossible de transporter plus.' (scene 37's wording, text/so_fr.tbl), then page wait and end."""
    .db 0x18, 0x36, 0x39, 0x38, 0x3C, 0x3C, 0x32, 0x2B, 0x35, 0x2E, 0x05, 0x2D, 0x2E, 0x05, 0x3D, 0x3B
    .db 0x2A, 0x37, 0x3C, 0x39, 0x38, 0x3B, 0x3D, 0x2E, 0x3B, 0x05, 0x39, 0x35, 0x3E, 0x3C, 0x5D
    .db 0x01, 0xFF, 0xFF
}

.alloc chest_found in code_c8 {
"""The French suffix, ' a été obtenu !' (text/so_fr.tbl), then page wait and end."""
    .db 0x05, 0x2A, 0x05, 0x48, 0x3D, 0x48, 0x05, 0x38, 0x2B, 0x3D, 0x2E, 0x37, 0x3E, 0x05, 0x5F
    .db 0x01, 0xFF, 0xFF
}
