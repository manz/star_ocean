"""
Sprite cels streamed without waiting for H-blank (notes/engine/battle_timing.md).

C3:917C starts each S-DD1 cel DMA (0x20 or 0x40 bytes into WRAM) right after a line's HDMA, so the DMA ends far
from the next one: CPU revision 1 consoles can crash when a DMA ends as HDMA starts. That wait is about half of
each stream's cost. Without it the battle runs faster on emulators, flash carts and later consoles; on an early
(1990-91) console it may crash. Off unless CEL_DMA_ANYTIME is set in a816.toml.
"""

.import "core/preamble"

.if CEL_DMA_ANYTIME {
; `lda #0x40 / bit $4212 / beq` before each `sta $4801`: a branch over the bit / beq.
    .macro skip_wait(address) {
        .alloc at address size 5 {
            bra _go
            nop
            nop
            nop
_go:
        }
    }

    skip_wait(0xC391D0)
    skip_wait(0xC3923F)
    skip_wait(0xC3925F)
    skip_wait(0xC39576)
    skip_wait(0xC39979)
    skip_wait(0xC39997)
}
