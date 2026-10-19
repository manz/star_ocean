"""
Party names in the dialog: [nick:] / [name:] inserts (string ids 00-17) copy the French name, already in
dialog codes (build/gen/dialog_names.bin, tools/encode_text.py), instead of converting the Japanese 8x8 name
from WRAM through C0:4B60. Ids 18+ (first letter of a name) keep the game's path.
"""

.import "core/preamble"

NAME_RECORD := 8  ; up to 7 codes, then 0xFF
REWIND := 0xFFFE  ; ends the insert: the stream goes back to the message

.alloc dialog_names in code_c0 {
    .incbin "dialog_names.bin"
}

; text_insert_string, ids below 0x18: `asl / tax / lda C2:3F21,x / tay / plx / jsr $3F51 / ply / rts`.
.alloc at 0xC23F14 size 13 {
    plx
    jsl dialog_insert_name
    ply
    rts
}

.alloc dialog_insert_name in code_c0 {
"""
A = string id (M16 X16, DB = $7E), X = insert buffer: the name's codes at X, X left on the REWIND written
    after them (as C2:3F51 leaves it). Out: A = name length.
"""
    phy
    txy  ; Y = destination
    asl
    asl
    asl
    tax  ; X = id * NAME_RECORD
    sep #0x20
_copy:
    lda.l dialog_names, x
    cmp #0xFF
    beq _end
    sta.w 0, y
    iny
    inx
    bra _copy
_end:
    rep #0x20
    txa
    and.w #NAME_RECORD - 1
    pha
    tyx
    lda.w #REWIND
    sta.w 0, x
    pla
    ply
    rtl
}
