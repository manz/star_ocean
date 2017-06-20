*=0xC80D38
    jsr.w shift_char
    jmp.w 0x0d41

*=0xC8FC00
.macro shift(delta) {
    lda.w 0x0020 + delta, x
    sta.l 0x004203
    nop
    nop
    rep #0x20
    lda.l 0x004216
    sep #0x20

    sta.w 0x0020 + delta, x
    xba

    ora.w 0x0000 + delta, x
    sta.w 0x0000 + delta, x
}

.macro copy(delta) {
    lda.w 0x0020 + delta, x
    sta.w 0x0000 + delta, x
}


shift_char:
{
    tya
    sec
    sbc.w #0x20
    tax
    phy
    sep #0x20
    lda.b #0x7F
    pha
    plb

    ldy.w #0x20

    lda.b 0x2e
    and.b #0x07
    beq raw_copy_loop

    jsr.w get_shift_value
    sta.l 0x004202

copy_loop:
    shift(0x0)
    shift(0x20)
    inx
    dey
    bne copy_loop
    bra _end

raw_copy_loop:
    copy(0x0)
    copy(0x20)
    inx
    dey
    bne raw_copy_loop

_end:
    ply
    rts
}

get_letter_width:
{
    phx
    tax
    cpx.w #0x00a6
    bmi _load_length
    lda.w #0x0008
    bra _end
 _load_length:

    lda.l length_table_copy, x
    and.w #0x00ff
    cmp.w #0x0008
    bcc _end
    lda.w #0x0008
_end:
    plx
    rts
}

update_letter_width_from_a:
    jsr.w get_letter_width
    pha
    clc
    adc.b 0x2e
    inc
    sta.b 0x2e
    pla
    clc
    adc.l 0x7ffffc
    sta.l 0x7ffffc
    rts

update_letter_width:
    lda.l 0x7ffffe
    jsr.w update_letter_width_from_a
    rts

update_letter_width_long:
    lda.l 0x7ffffe
    jsr.w update_letter_width
    rtl

update_letter_width_from_a_long:
    jsr.w get_letter_width
    clc
    adc.l 0x7ffffc
    sta.l 0x7ffffc
    rtl

get_shift_value:
    phx
    rep #0x20
    lda.b 0x2e
    and.w #0x0007
    tax
    sep #0x20
    lda.l shift_table, x
    plx
    rts

; Long call to dictionary_lookup (Baha MTE)
; used for anything but item descriptions.
dictionary_lookup_long:
     jsr.w 0xC8FB69
     rtl


this_is_the_end_C8FAB0:
