"""
The fight's top (or bottom) windows: enemy names, the party member's name / PV / PM, the L/R special moves.
The enemy window gives a cell to the L/R one, the party member window moving with it: 11 / 11 / 12 wide at
cells 0 / 10 / 20 instead of 12 / 11 / 11 at 0 / 11 / 21, so a special move's name has 9 cells (cells 22-30).
Each operand below is the `ldx #` (or `lda #` width) of a draw, in BG3 map offsets (2 bytes a cell, 0x40 a row).
"""

; Frames (`C1:527D`, top then bottom at X + 0x540): widths 12 / 11 / 11 at cells 0 / 11 / 21 become
; 11 / 11 / 12 at 0 / 10 / 20.
.alloc at 0xC1528B size 2 {  ; 0xC enemy window width
    .dw 0xB
}
.alloc at 0xC15299 size 2 {  ; 0x16 party member window at cell 10
    .dw 0x14
}
.alloc at 0xC152AA size 2 {  ; 0x2A L/R window at cell 20
    .dw 0x28
}
.alloc at 0xC152AD size 2 {  ; 0xB L/R window width
    .dw 0xC
}
.alloc at 0xC152D9 size 2 {  ; 0xC bottom: enemy window width
    .dw 0xB
}
.alloc at 0xC152E7 size 2 {  ; 0x556 bottom: party member window
    .dw 0x554
}
.alloc at 0xC152F8 size 2 {  ; 0x56A bottom: L/R window
    .dw 0x568
}
.alloc at 0xC152FB size 2 {  ; 0xB bottom: L/R window width
    .dw 0xC
}

; Enemy window contents one cell left (`C1:579B`). The party window's PV / PM rows (`C1:5402`, `C1:5842`) stay.
.alloc at 0xC157A7 size 2 {  ; 0x84
    .dw 0x82
}
.alloc at 0xC157B1 size 2 {  ; 0x44
    .dw 0x42
}
.alloc at 0xC157BD size 2 {  ; 0x5C4
    .dw 0x5C2
}
.alloc at 0xC157C7 size 2 {  ; 0x584
    .dw 0x582
}
.alloc at 0xC157F7 size 2 {  ; 0x84
    .dw 0x82
}
.alloc at 0xC157FC size 2 {  ; 0x5C4
    .dw 0x5C2
}

; Party member window contents one cell left (`C1:5473`: name, PV, `/`, max PV, PM, `/`, max PM).
; The bottom copy put the name and PV one cell right of the top one's; it takes the top's cells + 0x540.
.alloc at 0xC15496 size 2 {  ; 0x98 name
    .dw 0x96
}
.alloc at 0xC154B2 size 2 {  ; 0xD8 PV
    .dw 0xD6
}
.alloc at 0xC154DE size 2 {  ; 0xE2 max PV
    .dw 0xE0
}
.alloc at 0xC154F7 size 2 {  ; 0xE0 /
    .dw 0xDE
}
.alloc at 0xC15501 size 2 {  ; 0x11A PM
    .dw 0x118
}
.alloc at 0xC1552F size 2 {  ; 0x124 max PM
    .dw 0x122
}
.alloc at 0xC15548 size 2 {  ; 0x120 /
    .dw 0x11E
}
.alloc at 0xC15558 size 2 {  ; 0x5DA bottom: name
    .dw 0x5D6
}
.alloc at 0xC15574 size 2 {  ; 0x61A bottom: PV
    .dw 0x616
}
.alloc at 0xC155A0 size 2 {  ; 0x622 bottom: max PV
    .dw 0x620
}
.alloc at 0xC155B9 size 2 {  ; 0x620 bottom: /
    .dw 0x61E
}
.alloc at 0xC155C3 size 2 {  ; 0x65A bottom: PM
    .dw 0x658
}
.alloc at 0xC155F1 size 2 {  ; 0x662 bottom: max PM
    .dw 0x660
}
.alloc at 0xC1560A size 2 {  ; 0x660 bottom: /
    .dw 0x65E
}

; L/R window contents one cell left (`C1:5619`: the L / R labels, then the two special moves' names,
; 9 cells from cell 22).
.alloc at 0xC1564C size 2 {  ; 0x6C
    .dw 0x6A
}
.alloc at 0xC15656 size 2 {  ; 0xAC
    .dw 0xAA
}
.alloc at 0xC15660 size 2 {  ; 0xEC
    .dw 0xEA
}
.alloc at 0xC1566A size 2 {  ; 0x12C
    .dw 0x12A
}
.alloc at 0xC15674 size 2 {  ; 0x6C
    .dw 0x6A
}
.alloc at 0xC1567E size 2 {  ; 0xEC
    .dw 0xEA
}
.alloc at 0xC15688 size 2 {  ; 0xAE names
    .dw 0xAC
}
.alloc at 0xC15698 size 2 {  ; 0x5AC
    .dw 0x5AA
}
.alloc at 0xC156A2 size 2 {  ; 0x5EC
    .dw 0x5EA
}
.alloc at 0xC156AC size 2 {  ; 0x62C
    .dw 0x62A
}
.alloc at 0xC156B6 size 2 {  ; 0x66C
    .dw 0x66A
}
.alloc at 0xC156C0 size 2 {  ; 0x5AC
    .dw 0x5AA
}
.alloc at 0xC156CA size 2 {  ; 0x62C
    .dw 0x62A
}
.alloc at 0xC156D4 size 2 {  ; 0x5EE bottom: names
    .dw 0x5EC
}

; The bottom copy drew PV and max PV with 3 digits (`lda #3` before `C0:4501`), the top one with 4:
; 6746 showed as 746.
.alloc at 0xC15599 size 2 {  ; 3 PV digits
    .dw 4
}
.alloc at 0xC155B2 size 2 {  ; 3 max PV digits
    .dw 4
}
