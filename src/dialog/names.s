"""
Party names: the WRAM records at $7E:1548 (tools/party_names.py, build/gen/party_names.i). The dialog's [nick:] /
[name:] inserts read them as the game does (C2:3F21 slots, codes through C0:4B60), so a name the player enters
shows in the dialog.
"""

.import "core/preamble"

.include "party_names.i"

NAMES := 0x7E1548
RECORD := 12  ; name, 0xFF, nickname, 0xFF
ENTRY := 9  ; record, bytes to copy, name, 0xFF, padding
PARTY := 12

; C2:D85C, new game: filled each record from names8 through C0:41E4, which stops at nothing (a 7-letter French
; name ran over its 0xFF, nicknames were the name again). The French records instead.
.alloc at 0xC2D85C size 4 {
    jml.l party_names_init
}

.alloc party_names_init in code_c4 {
    php
    phb
    rep #0x30
    phx
    phy
    ldx.w #party_names_default & 0xFFFF
    ldy.w #NAMES & 0xFFFF
    lda.w #RECORD * PARTY - 1
    mvn party_names_default >> 16, NAMES >> 16
    ply
    plx
    plb
    plp
    rtl
}

; C2:D6E7, loading a save (M8 X16), after the records are copied from it: `jsl C2:D795`.
.alloc at 0xC2D6E7 size 4 {
    jsl party_names_fixup
}

.alloc party_names_fixup in code_c4 {
"""
A record holding a name an older save starts with (party_names_older) gets the French record, or its name alone.
X and Y kept: the caller goes on reading the save at Y.
"""
    php
    phb
    sep #0x20
    rep #0x10
    phx
    phy
    lda.b #party_names_older >> 16
    pha
    plb
    ldy.w #party_names_older & 0xFFFF
_entry:
    lda.w 0, y  ; record, 0xFF after the last entry
    cmp.b #0xFF
    beq _done
    rep #0x20
    and.w #0x00FF
    asl
    asl
    pha
    asl
    clc
    adc 1, s
    tax  ; X = record * RECORD
    pla
    sep #0x20
    phx
    phy
    iny
    iny
_compare:
    lda.w 0, y
    cmp.l NAMES, x
    bne _skip
    inx
    iny
    cmp.b #0xFF
    bne _compare
    ply
    plx
    phx
    phy
    lda.w 1, y  ; bytes to copy
    pha
_copy:
    lda.l party_names_default, x
    sta.l NAMES, x
    inx
    lda 1, s
    dec
    sta 1, s
    bne _copy
    pla
_skip:
    ply
    plx
    rep #0x20
    tya
    clc
    adc.w #ENTRY
    tay
    sep #0x20
    bra _entry
_done:
    ply
    plx
    plb
    plp
    jml.l 0xC2D795
}
