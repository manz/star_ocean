"""
Where menu labels sit (`ldx #label / ldy #row:column / jsr C3A5`), moved where the French needs room.
"""

.import "core/preamble"

; Save / load screens: "Choix d'un bloc" (EABB) from column 2 to 1, so "Choix d'un" fits its box.
.alloc at 0xCA7E02 size 3 {
    ldy.w #0x0201
}
.alloc at 0xCA7E24 size 3 {
    ldy.w #0x0201
}
; Name entry: "Choix d'un nom" (EAF1) from column 2 to 1 likewise.
.alloc at 0xCA88B5 size 3 {
    ldy.w #0x0201
}
; Its "Prénom" (EAEC) from column 2 to 1, clear of the name's first cell (column 5).
.alloc at 0xCA88DF size 3 {
    ldy.w #0x0401
}
; Its family name (FARRENCE, F99C...) from column 14 to 15: past the pad the name's letters start with
; (src/menu/vwf16.s FIXED_PAD), a gap after the last square.
.alloc at 0xCA8907 size 3 {
    ldy.w #0x040F
}
; Its letter grid: the Japanese scrolls an 8-row view (`$06AC`) over 22 rows of 10 characters (EC1D), `$06A8` =
; rows - `$06AC` + 1 scroll stops; the French set (EC1D, the grid rows F6E0-F6E7) is 8 rows, one view, no scrolling.
.alloc at 0xCA24DB size 3 {
    lda.w #0x0008
}

; Statut: the equipment slots' labels (EAB1, Arme ... Plat préféré) from column 1 to 0, so "Accessoire" clears the
; item names drawn at column 6.
.alloc at 0xCA7C11 size 3 {
    ldy.w #0x0100
}
; Its favourite dish's name, under "Plat préféré": column 1 to 0 with it.
.alloc at 0xCA7D9E size 3 {
    ldy.w #0x1100
}

; Équiper: the slots' labels (EA9C, Arme ... Accessoire) from column 2 to 1, so "Accessoire" clears the item names
; at column 7.
.alloc at 0xCA7840 size 3 {
    ldy.w #0x0101
}
; Its hand cursor (descriptor CA:0D94), x -4 and y + 4 for the seven slots, off the labels' first letter (the window
; starts at the screen edge, so the hand loses its first 4 px).
.alloc at 0xCA0D9E size 14 {
    .for slot := 0, 7 {
        .db 0xFC, 0x4C + slot * 0x0C
    }
}

; Shop tabs (EAD2 / EAD3, Achat Vente Fin): the hand cursor's (x, y) per tab, Japanese words 4 cells apart; the
; French ones at cells 0 / 5 / 10 (tools/vwf8.py STOPS), clear of the hand to their left.
.alloc at 0xCAF98B size 6 {
    .for tab := 0, 3 {
        .db tab * 0x28, 0x18
    }
}
; The pigeon shop's (EAD0, Achat Pigeon).
.alloc at 0xCAF999 size 4 {
    .for tab := 0, 2 {
        .db tab * 0x28, 0x18
    }
}

; The menu hand (CA:4C4E: sprite 0x70 + $06A6 at x $0696, y $0698) goes through an 8-bit x and never sets OAM's
; ninth x bit. A hand at x 0xF0 or more would be cut by the right edge, so that range now means x - 256: the bit is
; set there and cleared elsewhere, in the high table the game DMAs from $1F00.
.alloc at 0xCA4C73 size 3 {
    jsr.w menu_hand_cave
}

.alloc menu_hand_cave at 0xCAFFB3 size 0x4D {
    jsr.w 0x5456
    php
    rep #0x30
    lda.w 0x06A6
    and.w #0x00FF
    clc
    adc.w #0x0070
    pha
    lsr
    lsr
    tax
    pla
    and.w #0x0003
    tay
    lda.w #0x0001
_shift:
    dey
    bmi _bit
    asl
    asl
    bra _shift
_bit:
    sep #0x20
    pha
    lda.w 0x0696
    cmp.b #0xF0
    pla
    bcc _clear
    ora.l 0x001F00, x
    bra _store
_clear:
    eor.b #0xFF
    and.l 0x001F00, x
_store:
    sta.l 0x001F00, x
    plp
    rts
}

; Main menu and save screen party rows: "Suivant" (EA73, NEXT) from column 0x17 to 0x16, clear of the border.
.alloc at 0xCA7010 size 3 {
    ldy.w #0x0516
}
.alloc at 0xCA7E5D size 3 {
    ldy.w #0x0816
}

; Main menu commands ("Talents Bagage Groupe Régler" / "Équiper Savoirs Statut Sauver"): window x from 4 to 2,
; so "Régler" / "Sauver" fit.
.alloc at 0xCA6FA3 size 2 {
    lda.b #0x02
}

; Main menu hand cursor, (x, y) per command (descriptor CA:0278): one tile left of each command, which start at
; columns 0, 8, 16 and 23 of the labels (the Japanese had a 7-column stride).
.alloc at 0xCA0280 size 16 {
    .for row := 0, 2 {
        .db 0x00, 0x10 + row * 0x0C, 0x40, 0x10 + row * 0x0C, 0x80, 0x10 + row * 0x0C, 0xB8, 0x10 + row * 0x0C
    }
}

; Main menu: where the game greys "Sauver" when saving is off ($02EA >= 0): x, y, width, height from the window
; origin, palette 7. The Japanese covered three cells at x 0x15.
.alloc at 0xCA6FC8 size 2 {
    lda.b #0x17
}
.alloc at 0xCA6FD0 size 2 {
    lda.b #0x06
}

.macro button_icon(row, name_end) {
    """
    Settings, button icons: one sprite per row at x 0x98 + 8 * row in the Japanese (a staircase after the short
    names, over "Sélectionner" / "Annuler"); each now 4 px after its name and 2 px lower. `name_end` = screen x of
    the name's last pixel (measured), sprite x = object x - 8.
    """
    .alloc at 0xCA06B5 + row * 0x13 size 6 {
        lda.b #name_end + 4 + 8
        sta.b 0x22
        lda.b #0x68 + row * 0x0C + 2
    }
}
button_icon(0, 206)  ; Sélectionner
button_icon(1, 166)  ; Annuler
button_icon(2, 142)  ; Menu
button_icon(3, 158)  ; Cibler
button_icon(4, 175)  ; Arcane 1
button_icon(5, 175)  ; Arcane 2

; Settings, sound mode: the game lit a 5-cell rect at column 0x0E + 5 * mode; the French options are 6, 4 and 2
; cells wide (Stéréo Mono 3D).
.alloc at 0xCACE50 size 0x26 {
    lda.w 0x0715
    sta.b 0x30
    stz.b 0x31
    ldx.b 0x30
    lda.l sound_mode_rects, x
    sta.b 0x20
    lda.l sound_mode_rects + 3, x
    sta.b 0x22
    lda.b #0x09
    sta.b 0x21
    lda.b #0x02
    sta.b 0x23
    lda.b #0x03
    sta.b 0x24
    jsr.w 0xD23D
    rts
}

.alloc sound_mode_rects in code_c8 {
"""Column, then width, of Stéréo / Mono / 3D."""
    .db 0x0E, 0x15, 0x1A
    .db 0x06, 0x04, 0x02
}

; Groupe submenu (Stratégie / Échange / Formation): window at column 0x12, row 7, 8 + 1 columns wide (open and
; close), its dark HDMA fill 0x44 px wide; three columns more.
.alloc at 0xCA31FA size 3 {
    ldy.w #0x070B
}
.alloc at 0xCA3276 size 3 {
    ldy.w #0x070B
}
.alloc at 0xCA3257 size 2 {
    lda.b #0x44 + 3 * 8
}

; Combo screen, skill description: the Japanese drew the kanji name (16x16) and, on its right, its katakana reading
; in 8x8 (labels8 FA2A + skill, ids with bit 15 set). In French both are the name: always skip the reading.
.alloc at 0xCA9864 size 2 {
    bra 0xCA9887
}

; Combo screen, skill description: the range marker (CA:98B3, `lda #char / jsr A941`) is S (short) or L (long) in
; the Japanese; the French slots say C (courte) and L (longue), as the button labels (EB41).
.alloc at 0xCA98C9 size 2 {
    lda.b #0x43
}
.alloc at 0xCA98DB size 2 {
    lda.b #0x43
}
