"""
The ending staff roll in French. tools/ending_credits.py packs text/fr/ending_credits.toml into the game's C0:4C53
container (ending_credits.bin) and adds the accented letters the text uses to the roll's font: the S-DD1 sheet
(ending_font.bin), the character map (ending_map.bin, in place) and the glyph records (ending_glyphs.bin, the
original table plus the new ones; it ends at the code_c0 pool, so it moves and its readers follow).
"""

.import "core/preamble"
.import "menu/text16"

.alloc ending_credits_text in text16 {
    .incbin "ending_credits.bin"
ending_credits_text_end:
}

; C0:4C53 reads the container by a 16-bit offset in its bank.
.assert ending_credits_text >> 16 == ( ending_credits_text_end - 1 ) >> 16, "ending_credits_text crosses a bank"

.alloc ending_credits_font in text16 {
    .incbin "ending_font.bin"
}

.alloc ending_credits_glyphs in text16 {
    .incbin "ending_glyphs.bin"
}

; C0:6996: ASCII 0x20-0x7A to a glyph; the codes the roll never prints now name the accented letters.
.alloc at 0xC06996 size 0x5B {
    .incbin "ending_map.bin"
}

; C0:66EC: `ldy #$D8F0 / lda #$DE / jsl C0:4C53`, the roll's text unpacked to $7F:4000.
.alloc at 0xC066ED size 2 {
    .dw ending_credits_text & 0xFFFF
}
.alloc at 0xC066F0 size 1 {
    .db ending_credits_text >> 16
}

; C0:66BB: `ldx #$698A` / `lda #$DC`, the S-DD1 DMA of the sheet to $7F:0000.
.alloc at 0xC066BC size 2 {
    .dw ending_credits_font & 0xFFFF
}
.alloc at 0xC066C2 size 1 {
    .db ending_credits_font >> 16
}

; The glyph record readers, `lda long,x`: C0:6857 (rows, columns, tile), C0:6906 and C0:693E (advance).
.alloc at 0xC06860 size 3 {
    .dl ending_credits_glyphs + 1
}
.alloc at 0xC06869 size 3 {
    .dl ending_credits_glyphs + 2
}
.alloc at 0xC06872 size 3 {
    .dl ending_credits_glyphs + 3
}
.alloc at 0xC0690E size 3 {
    .dl ending_credits_glyphs
}
.alloc at 0xC06977 size 3 {
    .dl ending_credits_glyphs
}
