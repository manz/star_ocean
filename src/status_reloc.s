display_status:
loc_C6F72C:
    lda.w 0x3000, Y
    and.w #0x00ff
    cmp.w #0x000D             ; seems to be newline char
    beq loc_C6F76D
    cmp.w #0x00FF          ; end of string char
    beq loc_C6F77C
    sec                     ; ignore first 0x10 char
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
    tax                     ; computes font char index (c - 0x10) * 0x20
                            ; 2bpp 16px
    lda.b 0xdb
    clc
    adc.w #0x0020
    tay
    lda.w #0x003F ; '?'
    jsr.l copy_char
    plb
    ply
    plx
    jsr.w sub_C6F7B0
    iny
    bra loc_C6F72C
; ---------------------------------------------------------------------------
loc_C6F76D:                             ; CODE XREF: sub_C6F6F9+39j
    jsr.w handle_dangling_char

    lda.b 0x22
    clc
    adc.w #0x0080 ; 'Ç'
    sta.b 0x22
    tax
    iny
    bra loc_C6F72C
; ---------------------------------------------------------------------------
loc_C6F77C:                             ; CODE XREF: sub_C6F6F9+3Ej
    jsr.w handle_dangling_char

    plb
    plp
    rtl
