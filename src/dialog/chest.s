"""
Treasure chest message: `C2:05F2` builds it in $7E:6100 (colour, the item or the Fol amount, colour) and ended it
with the Japanese "を手に入れました。" written as immediates; the French suffix is copied there instead.
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

.alloc chest_found in code_c8 {
"""The French suffix, ' a été obtenu !' (text/so_fr.tbl), then page wait and end."""
    .db 0x05, 0x2A, 0x05, 0x48, 0x3D, 0x48, 0x05, 0x38, 0x2B, 0x3D, 0x2E, 0x37, 0x3E, 0x05, 0x5F
    .db 0x01, 0xFF, 0xFF
}
