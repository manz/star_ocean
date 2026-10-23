"""
Names found by id through a run table instead of a scan (notes/engine/battle_timing.md).

The names list (D7:06FA, 893 ids, 0 after the last) gives each id its entry; the offsets at D7:0000 follow in the
same order. Five copies of one reader (C0:3FBC, 40BF, 41F1, 49CF, CA:BE03) scan it an id at a time: about 8 us an
id passed, 0.8 ms for a battle name, a string drawn by C0:3FA3. Battle windows draw several at once, enough to
push a pass past its two frames. The ids form 20 runs of consecutive values with no id twice, so an id's entry is
its run's first entry plus its distance from the run's start: at most 20 tests, C0:3FA3 down to 0.1 ms. The lists
stay as they are; C8:1080 reads the entries after 0x1388 by position. Switched by NAME_INDEX in a816.toml.
"""

.import "core/preamble"

.if NAME_INDEX {
    NAME_ID := 0x20  ; direct page: the id the readers look for
    NAME_RUNS := 20

    .macro find_name_at(address) {
    """
    A reader's scan, `ldy #0 / rep #0x20` then the loop: 18 bytes, then the miss (`ply / plb / plp / rtl`)
    and, four bytes later, the hit reading the offset at $0000,y.
    """
        .alloc at address size 18 {
            rep #0x20
            jsl name_find
            bcs address + 22
            bra address + 18
            .for i := 0, 8 {
                nop
            }
        }
    }

    find_name_at(0xC03FBC)
    find_name_at(0xC040BF)
    find_name_at(0xC041F1)
    find_name_at(0xC049CF)
    find_name_at(0xCABE03)

    .alloc name_find in code_c4 {
"""
The entry of the id at NAME_ID (M16 X16). Out: carry set and Y = entry * 2, or carry clear and A = 0 (what the
scan left). X kept.
"""
        phx
        ldx.w #0x0000
_run:
        lda.b NAME_ID
        sec
        sbc.l name_runs.start, x
        cmp.l name_runs.count, x
        bcc _hit
        inx
        inx
        cpx.w #NAME_RUNS * 2
        bne _run
        plx
        lda.w #0x0000
        clc
        rtl
_hit:
        asl
        clc
        adc.l name_runs.offset, x
        tay
        plx
        sec
        rtl
    }

; The runs of D7:06FA in list order: first id, length, byte offset of the first entry (tests/test_name_index.py
; checks them against the ROM).
    .alloc name_runs in code_c4 {
        .scope name_runs {
start:
            .dw 0x0064, 0x09C4, 0x0001, 0x0011, 0x00C8, 0x1F40, 0x07D0, 0x0BB8, 0x0C38, 0x0C58
            .dw 0x0C98, 0x0CB8, 0x0CD8, 0x0CF8, 0x0D18, 0x0FA0, 0x0FAC, 0x0FB0, 0x1388, 0x2710
count:
            .dw 0x0012, 0x0008, 0x000D, 0x000D, 0x0002, 0x008A, 0x002A, 0x0010, 0x000A, 0x000C
            .dw 0x0009, 0x000A, 0x0009, 0x000C, 0x0009, 0x000A, 0x0002, 0x0002, 0x01FF, 0x002F
offset:
            .dw 0x0000, 0x0024, 0x0034, 0x004E, 0x0068, 0x006C, 0x0180, 0x01D4, 0x01F4, 0x0208
            .dw 0x0220, 0x0232, 0x0246, 0x0258, 0x0270, 0x0282, 0x0296, 0x029A, 0x029E, 0x069C
        }
    }
}
