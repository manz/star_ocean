"""
Faster battle loop routines (notes/engine/battle_timing.md). Busy fights run late: every routine here does what
the original does, in fewer cycles; `tools/battle_bench.py` scores them.

The two slot scans of the logic block test 64 slots each, one byte per slot, with a 16-bit step between two
8-bit tests: about 29 cycles an empty slot. Here they test 8 (or 4) slots per step at fixed offsets, 8 cycles an
empty one, and run the original body on a busy slot with X = that slot. Y is free: neither body reads it.

C5:035D finds an animation's current frame: entries of (duration byte, word) from [$BE], durations subtracted
from the time $20 until it goes negative; 0 ends (time back to 0), $FF loops (new time). It walks with three
`inc $BE` an entry; here Y walks, the subtraction stays in A: about 39 cycles an entry instead of 61.

C3:8F5E places one sprite piece in OAM, about 20 a frame, testing the object's rotation ($FA, $FC) and flips
($21 bits 7 and 6) on every piece. Objects without rotation or vertical flip get a loop without those tests; the
rest, and the rare paths (piece off screen, OAM full), stay on the original code.
"""

.import "core/preamble"

.if BATTLE_SPEEDUPS {
    BATTLE_FLAGS := 0xE2

    .macro test_slot(offset, next) {
    """One busy-slot test of an unrolled scan: A (8 bits) = the slot's first byte at X + offset."""
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

; C3:8F5E: one sprite piece. In: M8 X16, Y = the piece in the object's list, DB = $7E.
    .alloc at 0xC38F5E size 4 {
        jml oam_pieces
    }

    .alloc cel_call in code_c3 {
"""C3:917C (sprite cel stream) for the piece loop: jsl here. Out: carry as C3:917C left it."""
        jsr.w 0x917C
        rtl
    }

    .alloc oam_pieces in code_c4 {
"""C3:8F5E for objects without rotation or vertical flip; others go back to the original."""
        lda.b 0x21
        bmi _slow
        ldx.b 0xFA
        bne _slow
        ldx.b 0xFC
        beq _piece
_slow:
        lda.w 0x0000, y
        sta.b 0x28
        jml 0xC38F63
_piece:
        lda.w 0x0000, y
        sta.b 0x28
        ldx.b 0x10
        bit.b 0x21
; V = horizontal flip
        rep #0x20
        iny
        lda.w 0x0000, y
        sta.b 0x00
        bvs _flip
        clc
        adc.b 0x22
_x:
        cmp.w #0xFFF0
        bcs _x_in
        cmp.w #0x0100
        bcc _x_in
        jml 0xC38FFC
_flip:
        lda.b 0x28
        bne _flip16
        lda.b 0x22
        sec
        sbc.b 0x00
        sec
        sbc.w #0x0008
        bra _x
_flip16:
        lda.b 0x22
        sec
        sbc.b 0x00
        sec
        sbc.w #0x0010
        bra _x
_x_in:
        ror.b 0x14
        sta.b 0x00, x
        inx
        iny
        iny
        lda.w 0x0000, y
        sta.b 0x00
        clc
        adc.b 0x24
        sta.b 0x00, x
        bpl _y_below
        cmp.w #0xFFF0
        bcs _y_in
        jml 0xC39023
_y_below:
        cmp.w #0x00E0
        bcc _y_in
        jml 0xC39023
_y_in:
        inx
        iny
        iny
        lda.b 0x30
        bne _no_cel
        jsl cel_call
        bcc _next
        asl.b 0x14
        jml 0xC39096
_no_cel:
        lda.w 0x0000, y
        ora.b 0x20
        sta.b 0x00, x
        inx
        inx
        iny
        iny
_next:
        lda.b 0x28
        lsr
        ror.b 0x14
        stx.b 0x10
        cpx.w #0x1EFC
        bne _room
        jml 0xC39096
_room:
        sep #0x20
        dec.b 0x16
        bne _count
; 8 pieces: their high-table bits go out
        ldx.b 0x12
        rep #0x20
        lda.b 0x14
        sta.b 0x00, x
        stz.b 0x14
        sep #0x20
        inx
        inx
        stx.b 0x12
        lda.b #0x08
        sta.b 0x16
_count:
        dec.b 0x2E
        beq _done
        jmp.w _piece
_done:
        jml 0xC3908F
    }
}
