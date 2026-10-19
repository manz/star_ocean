"""
Where menu labels sit (`ldx #label / ldy #row:column / jsr C3A5`), moved where the French needs room.
"""

; Save / load screens: "Choix d'un bloc" (EABB) from column 2 to 1, so "Choix d'un" fits its box.
.alloc at 0xCA7E02 size 3 {
    ldy.w #0x0201
}
.alloc at 0xCA7E24 size 3 {
    ldy.w #0x0201
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
