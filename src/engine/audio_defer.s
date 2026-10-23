"""
Battle audio sent while the main loop waits instead of from the IRQ (notes/engine/battle_timing.md).

In battle the line-258 IRQ calls C0:032D every frame: it streams sound data to the SPC700 in 3-byte handshakes, up
to 8% of a frame, and steals that time from whatever pass is running. Here the IRQ only marks the send pending and
C0:84AB (the pass's wait for the line-216 IRQ) sends it. A send still pending at the next line-258 IRQ goes from
the IRQ as before: one send a frame, at most a frame late. Off unless AUDIO_DEFERRED is set in a816.toml.
"""

.import "core/preamble"

.if AUDIO_DEFERRED {
    LAST_SEND_LINE := 160  ; a send takes up to about 20 lines
    .struct AudioDefer {
        byte pending  ; 1: a send waits for the main loop
    }


    .reserve audio_defer as AudioDefer in sram

; C0:02C8: the battle IRQ's `jsr $032D`.
    .alloc at 0xC002C8 size 3 {
        jsr.w audio_mark
    }

    .alloc audio_mark in code_c0 {
"""In the line-258 IRQ (M8 X16, D and DB 0): send last frame's audio if the main loop never did, mark this one."""
        lda.l audio_defer.pending
        beq _mark
        jsr.w 0x032D
        sep #0x20
_mark:
        lda.b #0x01
        sta.l audio_defer.pending
        rts
    }

; C0:84AB: wait for $D9 to clear, then to be set (the line-216 IRQ).
    .alloc at 0xC084AB size 4 {
        jml audio_wait
    }

    .alloc audio_wait in code_c0 {
"""C0:84AB, sending pending audio while it waits. Out: rtl, P as the caller had it."""
        php
        sep #0x20
_clear:
        jsr.w _send
        lda.b 0xD9
        bne _clear
_set:
        jsr.w _send
        lda.b 0xD9
        beq _set
        plp
        rtl

_send:
; claimed before sending, so the IRQ never runs C0:032D at the same time
        lda.l audio_defer.pending
        beq _none
; only with room before the line-216 IRQ: a late send would eat the forced-blank DMA window
        lda.b #0xFF
        sta.l 0x004201
        lda.l 0x002137
        lda.l 0x00213F
        lda.l 0x00213D
        xba
        lda.l 0x00213D
        and.b #0x01
        xba
        rep #0x20
        cmp.w #LAST_SEND_LINE
        sep #0x20
        bcs _none
        lda.b #0x00
        sta.l audio_defer.pending
        php
        rep #0x30
        pha
        phx
        phy
        phb
        phd
        lda.w #0x0000
        tcd
        sep #0x20
        pha
        plb
        jsr.w 0x032D
        rep #0x30
        pld
        plb
        ply
        plx
        pla
        plp
_none:
        rts
    }
}
