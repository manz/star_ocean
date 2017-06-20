display_description_text:                           ; CODE XREF: sub_CABB07+7P
{
    php
    phb
    sep #0x20
;.A8
    pha
    rep #0x20
;.A16
    stz.b 0x2e
    sta.b 0x20

    lda.w #0x0000
    sta.l 0x7ffffc ; clear line length

    lda.b 0x06
    xba
    and.w #0xFF00
    asl
    asl
    sta.b 0x00
    stx.b 0x22
    plb

    jsr.w clear_all_lines

loc_C6F7E9:                             ; CODE XREF: display_item+57j
                                         ; display_item+64j
    lda.w 0x0000, Y
    cmp.w #0x000d
    beq loc_C6F82A
    cmp.w #0x0010
    beq line_return_auto
_continue:
    cmp.w #0xffff
    beq loc_C6F837
    sec
    sbc.w #0x0010
    sta.l 0x7ffffe
    asl
    asl
    asl
    asl
    asl
    phx
    phy
    phb
    tax
    lda.b 0xdb
    clc
    adc.w #0x0020                       ; write next char with 0x20 offset and shift & merge after
    tay
    lda.w #0x003f
    jsr.l copy_char
    plb
    ply
    plx

    jsr.w sub_C6F7B0
    iny
    iny
    bra loc_C6F7E9
; ---------------------------------------------------------------------------

loc_C6F82A:                             ; CODE XREF: display_item+1Ej
    jsr.w handle_dangling_char

    lda.w #0x0000
    sta.l 0x7ffffc ; clear line length

    lda.b 0x22
    clc
    adc.w #0x0080
    sta.b 0x22
    tax
;    jsr.w clear_line
    iny
    iny
    bra loc_C6F7E9
; ---------------------------------------------------------------------------

loc_C6F837:                             ; CODE XREF: display_item+23j
    jsr.w handle_dangling_char

    plb
    plp
    rtl

line_return_auto:
{
;    jsr.l update_letter_width_from_a_long

    pha
    phx
    phy
    lda.l 0x7ffffc
    pha
peek_next_char:

    lda.w 0x0002, y
    cmp.w #0xffff   ; \0
    beq return_test
    cmp.w #0x000d   ; \n
    beq return_test
    cmp.w #0x0010   ; \s
    beq return_test
    sec
    sbc.w #0x0010

    jsr.l update_letter_width_from_a_long
    iny
    iny
    bra peek_next_char

return_test:
    lda.l 0x7ffffc
    cmp.w #(30 - 6) * 8 ; line size in pixels
    bcc no_return
    pla
    sta.l 0x7ffffc
    ply
    plx
    pla
    jmp.w loc_C6F82A ; force new line fucker and continue
    jmp.w peek_next_char

no_return:
    pla
    sta.l 0x7ffffc
    ply
    plx
    pla
    jmp.w _continue
}

clear_all_lines:
{
    phx
    phy
    ldx.b 0x22
    ldy.w #30
    lda.w #198
_continue:
    sta.l 0x7E0000, X
    sta.l 0x7E0040, X
    sta.l 0x7E0000 + 0x80, X
    sta.l 0x7E0040 + 0x80, X
    sta.l 0x7E0000 + 0x80 * 2, X
    sta.l 0x7E0040 + 0x80 * 2, X
    inx
    inx
    dey
    bne _continue
    ply
    plx
    rts
}
;clear_line:
;{
;    phx
;    phy
;    ldx.b 0x22
;    ldy.w #30
;    lda.w #198
;_continue:
;    sta.l 0x7E0000, X
;    sta.l 0x7E0040, X
;    inx
;    inx
;    dey
;    bne _continue
;    ply
;    plx
;    rts
;}
}

handle_dangling_char:
{
    lda.b 0x2e
    beq _end
    ; if we have consider the tile full and add it to the tilemap.
    lda.w #0x0008
    sta.b 0x2e
    jsr.w sub_C6F7B0
_end:

    stz.b 0x2e
    rts
}
