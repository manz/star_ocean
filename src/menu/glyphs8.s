"""
Fixed tiles the menu code prints itself (CA:A941: tile = char - 0x20), where the French 8x8 font moved them.
"""

SLASH := 0xCF  ; tile 0xAF: the big HP / MP slash (Japanese tile 0x41 is a letter now)

; HP / MP "cur / max" on the main menu: `ldy #pos / lda #0x61 / jsr A941`.
.for site := 0, 4 {
    .alloc at 0xCA7097 + site * 8 size 2 {
    lda.b #SLASH
    }
}
