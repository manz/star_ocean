"""
Dialog VWF: the 8x16 katsuji font in place of the 16x16 glyphs, advanced by each glyph's width.

`text_blit_glyph` (C2:63A0) keeps its pipeline: shift by the pen's sub-tile x, compose, merge into the
framebuffer. Two hooks: the glyph fetch fills its 16x16 buffer from the katsuji record, and the pen advances by
the record's width + 1 instead of 12.
"""

.import "core/preamble"

FONT_RECORD := 17  ; katsuji 8x16: 16 rows 1bpp + advance width
FONT_GLYPHS := 0x80  ; codes below 0x80 take one byte in the stream
GLYPH_CODE := 5  ; stream code = glyph + 5
UNKNOWN_CODE := 0x60  ; "?" in text/so_fr.tbl

; The kanji tail of the 16x16 font (glyphs 0x5FC-0x63F): read with the F window on page 3, as the blit's own
; FF: fetch is.
.alloc dialog_font at 0xFFBF80 size FONT_GLYPHS * FONT_RECORD {
    .incbin "dialog_font_low.bin"
}

.reserve dialog_advance 1 in sram

; Glyph fetch: `lda 0,y / sta $31` x 16 from FF:(glyph * 32), then clear $51-$5F.
.alloc at 0xC263B4 {
    jsl dialog_glyph_load
    jmp 0x6414
}

; Pen: `lda $D9 / clc / adc #$0C / adc $DB / sta $D9`.
.alloc at 0xC265B9 size 9 {
    jsl dialog_advance_pen
    nop
    nop
    nop
    nop
    nop
}

; Line measure (C2:4134): a line ended after 17 glyphs, the Japanese window's width. The French text is reflowed
; to the window's pixels at build time (tools/encode_text.py), so only a newline or page ends a line.
.alloc at 0xC2416A size 3 {
    cmp.w #0xFF
}

; Letter spacing ($03DB) was 1 on lines under 17 glyphs: the VWF advance already has its 1 px gap.
.alloc at 0xC24122 size 2 {
    lda #0
}

.alloc dialog_glyph_load in code_c0 {
"""
Y = glyph * 32 (M16 X16, D = $0300, DB = $FF): the glyph's rows into the blit's left column
    $0331-$0340, its right column and spill $0341-$0360 cleared, its width into dialog_advance. The rows go in
    1 px right: the shadow's left pixel lands in column 0, not off the blit's 24 px window.
"""
    tya
    lsr
    lsr
    lsr
    lsr
    lsr
    clc
    adc.w #GLYPH_CODE
    cmp.w #FONT_GLYPHS
    bcc _in_font
    lda.w #UNKNOWN_CODE  ; a code the font lacks (an untranslated insert): never read past the font
_in_font:
    pha
    asl
    asl
    asl
    asl
    clc
    adc 1, s
    tax  ; code * 17
    pla
    .for row := 0, 8 {
        lda.w ( dialog_font & 0xFFFF ) + row * 2, x
        sta 0x31 + row * 2
    }
    .for word := 0, 16 {
        stz 0x41 + word * 2
    }
    sep #0x20
    lda.w ( dialog_font & 0xFFFF ) + 16, x
    sta.l dialog_advance
    ldx.w #15
_shift:
    lsr 0x31, x
    ror 0x41, x
    dex
    bpl _shift
    rep #0x20
    rtl
}

.alloc dialog_advance_pen in code_c0 {
"""M8, D = $0300: pen x ($03D9) += glyph width + 1 + letter spacing ($03DB)."""
    lda 0xD9
    sec
    adc.l dialog_advance
    clc
    adc 0xDB
    sta 0xD9
    rtl
}
