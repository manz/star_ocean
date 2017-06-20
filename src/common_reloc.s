sub_C6F7B0:                             ; CODE XREF: sub_C6F654:loc_C6F68Ep
;                                         sub_C6F6A5:loc_C6F6E2p ...
{
    phx
    jsr.l update_letter_width_long
    plx
loop:
    lda.b 0x2e
    cmp.w #0x0008
    bcc end
    lda.b 0xdd
    clc
    adc.w #0x0114
    clc
    adc.b 0x00
    sta.l 0x7E0000, X
    inc
    sta.l 0x7E0040, X

    inc 0xdd
    inc 0xdd

    lda 0xdb
    clc
    adc.w #0x20
    sta 0xdb

    inx
    inx

    lda.b 0x2e
    sec
    sbc.w #0x0008
    sta.b 0x2e
    bne loop
end:
    rts
}
