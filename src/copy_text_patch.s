; updates copy text
; used by other things than descriptions
*=0xCAACCC
{
    php
    rep #0x20
loc_CAACCF:
    lda.w 0x3000, Y
    and.w #0x00ff
    cmp.w #0x00ff
    beq _exit
    cmp.w #0x00f0
    bcc _store
    iny
    jsr.l dictionary_lookup_long
    bra loc_CAACCF
_store:
    sta.l 0x7ec1b3, X
    inx
    inx
    iny
    bra loc_CAACCF
_exit:
    lda #0xffff
    sta.l 0x7ec1b3, X
    sep #0x20
    plp
    rts
}

; updates copy text to avoid line returns on a fixed line length
; used for descriptions
*=0xCAB382                             ; CODE XREF: sub_CAB37A+3p
{
    php
    rep #0x20

loc_CAB385:                             ; CODE XREF: sub_CAB382+12j
    lda [0x28]
    sta [0x2c]
    inc 0x28
    inc 0x28
    inc 0x2c
    inc 0x2c
    cmp #0xffff
    bne loc_CAB385
    sep #0x20
    plp
    rts
}
