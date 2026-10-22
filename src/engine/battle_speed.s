"""
Faster battle loop routines (notes/engine/battle_timing.md). Busy fights run late: every routine here does what
the original does, in fewer cycles; `tools/battle_bench.py` scores them.

The two slot scans of the logic block test 64 slots each, one byte per slot, with a 16-bit step between two
8-bit tests: about 29 cycles an empty slot. Here they test 8 (or 4) slots per step at fixed offsets, 8 cycles an
empty one, and run the original body on a busy slot with X = that slot. Y is free: neither body reads it.

C5:035D finds an animation's current frame: entries of (duration byte, word) from [$BE], durations subtracted
from the time $20 until it goes negative; 0 ends (time back to 0), $FF loops (new time). It walks with three
`inc $BE` an entry; here Y walks, the subtraction stays in A: about 39 cycles an entry instead of 61.
"""

.import "core/preamble"

.if BATTLE_SPEEDUPS {
    BATTLE_FLAGS := 0xE2

; One busy-slot test of an unrolled scan: A (8 bits) = the slot's first byte at X + offset.
    .macro test_slot(offset, next) {
        lda.w offset, x
        beq next
        ldy.w #offset
        jsr.w _busy
    }

; C0:5121: the $20-byte slots at $7E:B073 (64), C0:51F3 on each busy one.
    .alloc at 0xC05121 size 4 {
        jml scan_b073
    }

    .alloc scan_b073 in code_c0 {
"""C0:5121, unrolled. In: X16. Out: rtl, P and DB as the caller had them."""
        php
        phb
        sep #0x20
        lda.b #0x7E
        pha
        plb
        lda.b BATTLE_FLAGS
        bit.b #0x81
        bne _done
        ldx.w #0xB073
_step:
        test_slot(0x00, _1)
_1:
        test_slot(0x20, _2)
_2:
        test_slot(0x40, _3)
_3:
        test_slot(0x60, _4)
_4:
        test_slot(0x80, _5)
_5:
        test_slot(0xA0, _6)
_6:
        test_slot(0xC0, _7)
_7:
        test_slot(0xE0, _8)
_8:
        rep #0x20
        txa
        clc
        adc.w #0x0100
        tax
        sep #0x20
        cpx.w #0xB873
        bne _step
_done:
        plb
        plp
        rtl

_busy:
; X = the step's first slot, Y = the busy one's offset: the original body with X = that slot
        phx
        rep #0x20
        tya
        clc
        adc 1, s
        tax
        sep #0x20
        lda.b BATTLE_FLAGS
        bit.b #0xC0
        beq _call
        lda.w 0x0000, x
        cmp.b #0x72
        bcs _skip
_call:
        jsr.w 0x51F3
        sep #0x20
_skip:
        plx
        rts
    }

; C1:80E5: the $40-byte slots at $7E:C073 (64), a handler each by its first byte (C1:8135, from 1).
    .alloc at 0xC180E5 size 4 {
        jml scan_c073
    }

    .alloc scan_c073 in code_c1 {
"""C1:80E5, unrolled. In: X16. Out: rtl, P and DB as the caller had them."""
        php
        phb
        sep #0x20
        lda.b #0x7E
        pha
        plb
        ldx.w #0xC073
_step:
        test_slot(0x00, _1)
_1:
        test_slot(0x40, _2)
_2:
        test_slot(0x80, _3)
_3:
        test_slot(0xC0, _4)
_4:
        rep #0x20
        txa
        clc
        adc.w #0x0100
        tax
        sep #0x20
        cpx.w #0xD073
        bne _step
        plb
        plp
        rtl

_busy:
        phx
        rep #0x20
        tya
        clc
        adc 1, s
        tax
        sep #0x20
        lda.w 0x0000, x
        cmp.b #0x11
        beq _run
        cmp.b #0x12
        beq _run
        cmp.b #0x10
        beq _run
        lda.b BATTLE_FLAGS
        bit.b #0x81
        bne _skip
        bit.b #0x40
        beq _run
        lda.w 0x0000, x
        cmp.b #0x7B
        bcc _skip
_run:
        txy
        lda.w 0x0000, x
        dec
        rep #0x20
        and.w #0x00FF
        asl
        tax
        jsr.w (0x8135, x)
        sep #0x20
_skip:
        plx
        rts
    }

; C5:035D: the animation frame lookup, 9 calls and about 30 entries a frame in a busy fight.
    .alloc at 0xC5035D size 4 {
        jml anim_frame
    }

    .alloc anim_frame in code_c5 {
"""
C5:035D, Y-indexed. In: M16 X16, A = script (bank in $C0), $20 = time. Out: rtl, A = the frame's word,
$BE = its address, $00 = time left, $02 = its duration, $10 = script; X and Y kept.
"""
        cmp.w #0x0000
        bne _go
        rtl
_go:
        sta.b 0xBE
        sta.b 0x10
        phy
        ldy.w #0x0000
        lda.b 0x20
_first:
; the first entry's duration is not tested for 0 / $FF
        sta.b 0x00
        lda [0xBE], y
        and.w #0x00FF
        bra _sub
_next:
        iny
        iny
        iny
        sta.b 0x00
        lda [0xBE], y
        and.w #0x00FF
        beq _end
        cmp.w #0x00FF
        beq _loop
_sub:
; A = $00 - duration
        eor.w #0xFFFF
        sec
        adc.b 0x00
        bpl _next
        sta.b 0x00
        lda [0xBE], y
        and.w #0x00FF
        sta.b 0x02
        iny
        tya
        clc
        adc.b 0xBE
        sta.b 0xBE
        ply
        lda [0xBE]
        rtl
_end:
        stz.b 0x20
        stz.b 0x02
        lda.b 0x10
        inc
        sta.b 0xBE
        ply
        lda [0xBE]
        rtl
_loop:
        iny
        lda [0xBE], y
        sta.b 0x20
        ldy.w #0x0000
        bra _first
    }
}
