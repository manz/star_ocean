"""
The fight's command ring labels in French (tools/ring_labels.py): SPECIAL, ITEM, RUN, TACTICS and CHANGE become
SPECIAL, OBJET, FUIR, TACTIQUE and ECHANGE. Each label is a sprite frame of 8x8 cels (C1:4F50 holds the frame
pointers); the frames stay, every cel record's 24-bit source points at its new S-DD1 stream: cel n of the five labels,
in frame order, at ring_labels + 0x40 * n.
"""

.import "core/preamble"
.import "menu/text16"

.alloc ring_labels in text16 {
    .incbin "ring_labels.bin"
}

; SPECIAL: the frame at C1:5052.
.alloc at 0xC1505A size 3 {
    .dl ring_labels + 0x000
}
.alloc at 0xC15062 size 3 {
    .dl ring_labels + 0x040
}
.alloc at 0xC1506A size 3 {
    .dl ring_labels + 0x080
}
.alloc at 0xC15072 size 3 {
    .dl ring_labels + 0x0C0
}

; OBJET: the frame at C1:5075.
.alloc at 0xC1507D size 3 {
    .dl ring_labels + 0x100
}
.alloc at 0xC15085 size 3 {
    .dl ring_labels + 0x140
}
.alloc at 0xC1508D size 3 {
    .dl ring_labels + 0x180
}

; FUIR: the frame at C1:5090.
.alloc at 0xC15098 size 3 {
    .dl ring_labels + 0x1C0
}
.alloc at 0xC150A0 size 3 {
    .dl ring_labels + 0x200
}

; TACTIQUE: the frame at C1:50A3.
.alloc at 0xC150AB size 3 {
    .dl ring_labels + 0x240
}
.alloc at 0xC150B3 size 3 {
    .dl ring_labels + 0x280
}
.alloc at 0xC150BB size 3 {
    .dl ring_labels + 0x2C0
}
.alloc at 0xC150C3 size 3 {
    .dl ring_labels + 0x300
}

; ECHANGE: the frame at C1:50C6.
.alloc at 0xC150CE size 3 {
    .dl ring_labels + 0x340
}
.alloc at 0xC150D6 size 3 {
    .dl ring_labels + 0x380
}
.alloc at 0xC150DE size 3 {
    .dl ring_labels + 0x3C0
}
.alloc at 0xC150E6 size 3 {
    .dl ring_labels + 0x400
}
