"""
Treasure chest message: `C2:05F2` builds it in $7E:6100 (colour, the item or the Fol amount, colour) and ended it
with the Japanese "を手に入れました。" written as immediates; the French suffix is copied there instead. The field
item find (syscall 55, `C6:DD40`) and the multi-item find (`C6:DAD7`, up to three items joined by "、") build the
same message the same way and get the same suffix. `C2:5169` wrote a whole message as immediates ("持ち物がいっぱい
です", the inventory is full).
"""

.import "core/preamble"

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

; C6:DB26: between two items of the list (M16, X = the stream); was "、" stored in 8-bit mode.
.alloc at 0xC6DB26 size 0x0A {
    lda.w #0x055E  ; ", " (text/so_fr.tbl)
    sta.w 0x0000, x
    inx
    inx
    bra _item_list_next
}

.label _item_list_next = 0xC6DB30

; C6:DB75: X = where the list's suffix goes (DB = $7E, M16 X16); the routine then ends with `plb / rts`.
.alloc at 0xC6DB75 size 0x2C {
    txy
    ldx.w #chest_found & 0xFFFF
    lda.w #sizeof(chest_found) - 1
    mvn chest_found >> 16, 0x7E
    plb
    rts
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
