"""
The fight's item list (`C1:2EDD`, 2 columns of 2 rows) laid out as the field's Bagage: the second column 16 cells
right of the first, not 14, so its icon, name, `:` and count sit at cells 18 / 19 / 27 / 28-29 as the field menu's
do, and the names get the two cells the field's have before the `:`.
"""

; After each item: `adc #0x1C` to the next column.
.alloc at 0xC12FE8 size 2 {
    .dw 0x20
}
; After the second column: `adc #0x48` back to the first column, two rows down (0x80 from the row's start).
.alloc at 0xC12FF5 size 2 {
    .dw 0x80 - 2 * 0x20
}
; The hand's x: column * 112 (`asl` x 3 of column * 16, `sec / sbc $04`), then `adc $00` (+1 with the carry set):
; column * 128 + 1 instead, 16 cells a column.
.alloc at 0xC1330E size 2 {
    nop
    nop
}
