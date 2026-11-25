"""
The fight's popup words in French (tools/battle_obj.py): the battle sprite sheet's S-DD1 stream, D9:0000 in the
game, redrawn: Short / Long (the L / R special's range) become Court / Long, Guard Garde, Guts!! Cran!!, Heal Soin,
MISS!! Raté!!. The new letters pack 5 bytes past the game's 4038 and the next stream follows it, so the stream moves
to the text16 pool and its loader (C0:23C3, run with each map load, its only reader) points there.
"""

.import "core/preamble"
.import "menu/text16"

.alloc battle_obj in text16 {
    .incbin "battle_obj.bin"
}

; `ldx #0x0000` / `stx 0x4302`: the DMA source address the S-DD1 reads.
.alloc at 0xC023D3 size 2 {
    .dw battle_obj & 0xFFFF
}

; `lda #0xD9` / `sta 0x4304`: its bank.
.alloc at 0xC023D9 size 1 {
    .db battle_obj >> 16
}
