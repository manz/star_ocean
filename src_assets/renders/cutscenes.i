.pool cutscene_frames {
    range 0xCC2C4E 0xCC2D26
    range 0xCC2D72 0xCC2D94
    range 0xCC2DE0 0xCC2DFA
    range 0xCC2F31 0xCC308C
    range 0xCC30B8 0xCC3337
    range 0xCCFC60 0xCCFFFF
    strategy pack
}
.alloc cutscene_00_00 in text16 {
    .incbin "cutscene_00_00_top.bin"
    .incbin "cutscene_00_00_bottom.bin"
}
.alloc cutscene_00_01 in text16 {
    .incbin "cutscene_00_01_top.bin"
    .incbin "cutscene_00_01_bottom.bin"
}
.alloc cutscene_00_02 in text16 {
    .incbin "cutscene_00_02_top.bin"
    .incbin "cutscene_00_02_bottom.bin"
}
.alloc cutscene_00_03 in text16 {
    .incbin "cutscene_00_03_top.bin"
    .incbin "cutscene_00_03_bottom.bin"
}
.alloc cutscene_00_04 in text16 {
    .incbin "cutscene_00_04_top.bin"
    .incbin "cutscene_00_04_bottom.bin"
}
.alloc cutscene_00_05 in text16 {
    .incbin "cutscene_00_05_top.bin"
    .incbin "cutscene_00_05_bottom.bin"
}
.alloc cutscene_00 in cutscene_frames {
    .db 6, 0x0b, 0x07
    .db 1
    .dw 8 & 0xFFFF, 4 & 0xFFFF
    .dl cutscene_00_00
    .db 11
    .db 1
    .dw 24 & 0xFFFF, 4 & 0xFFFF
    .dl cutscene_00_01
    .db 20
    .db 1
    .dw 40 & 0xFFFF, 4 & 0xFFFF
    .dl cutscene_00_02
    .db 12
    .db 1
    .dw 8 & 0xFFFF, 20 & 0xFFFF
    .dl cutscene_00_03
    .db 19
    .db 1
    .dw 24 & 0xFFFF, 20 & 0xFFFF
    .dl cutscene_00_04
    .db 23
    .db 1
    .dw 40 & 0xFFFF, 20 & 0xFFFF
    .dl cutscene_00_05
    .db 19
}
.alloc at 0xCC090F size 2 {
    .dw cutscene_00 & 0xFFFF
}
.assert cutscene_00 >> 16 == 0xCC, "cutscene_00: sprite frames are read from bank CC"
.alloc cutscene_01_00 in text16 {
    .incbin "cutscene_01_00_top.bin"
    .incbin "cutscene_01_00_bottom.bin"
}
.alloc cutscene_01_01 in text16 {
    .incbin "cutscene_01_01_top.bin"
    .incbin "cutscene_01_01_bottom.bin"
}
.alloc cutscene_01_02 in text16 {
    .incbin "cutscene_01_02_top.bin"
    .incbin "cutscene_01_02_bottom.bin"
}
.alloc cutscene_01_03 in text16 {
    .incbin "cutscene_01_03_top.bin"
    .incbin "cutscene_01_03_bottom.bin"
}
.alloc cutscene_01_04 in text16 {
    .incbin "cutscene_01_04_top.bin"
    .incbin "cutscene_01_04_bottom.bin"
}
.alloc cutscene_01_05 in text16 {
    .incbin "cutscene_01_05_top.bin"
    .incbin "cutscene_01_05_bottom.bin"
}
.alloc cutscene_01_06 in text16 {
    .incbin "cutscene_01_06_top.bin"
    .incbin "cutscene_01_06_bottom.bin"
}
.alloc cutscene_01_07 in text16 {
    .incbin "cutscene_01_07_top.bin"
    .incbin "cutscene_01_07_bottom.bin"
}
.alloc cutscene_01 in cutscene_frames {
    .db 8, 0x13, 0x07
    .db 1
    .dw -8 & 0xFFFF, 8 & 0xFFFF
    .dl cutscene_01_00
    .db 12
    .db 1
    .dw 8 & 0xFFFF, 8 & 0xFFFF
    .dl cutscene_01_01
    .db 9
    .db 1
    .dw 24 & 0xFFFF, 8 & 0xFFFF
    .dl cutscene_01_02
    .db 15
    .db 1
    .dw 40 & 0xFFFF, 8 & 0xFFFF
    .dl cutscene_01_03
    .db 15
    .db 1
    .dw 56 & 0xFFFF, 8 & 0xFFFF
    .dl cutscene_01_04
    .db 8
    .db 1
    .dw 8 & 0xFFFF, 24 & 0xFFFF
    .dl cutscene_01_05
    .db 18
    .db 1
    .dw 24 & 0xFFFF, 24 & 0xFFFF
    .dl cutscene_01_06
    .db 16
    .db 1
    .dw 40 & 0xFFFF, 24 & 0xFFFF
    .dl cutscene_01_07
    .db 15
}
.alloc at 0xCC0914 size 2 {
    .dw cutscene_01 & 0xFFFF
}
.assert cutscene_01 >> 16 == 0xCC, "cutscene_01: sprite frames are read from bank CC"
.alloc cutscene_02_00 in text16 {
    .incbin "cutscene_02_00_top.bin"
    .incbin "cutscene_02_00_bottom.bin"
}
.alloc cutscene_02_01 in text16 {
    .incbin "cutscene_02_01_top.bin"
    .incbin "cutscene_02_01_bottom.bin"
}
.alloc cutscene_02_02 in text16 {
    .incbin "cutscene_02_02_top.bin"
    .incbin "cutscene_02_02_bottom.bin"
}
.alloc cutscene_02_03 in text16 {
    .incbin "cutscene_02_03_top.bin"
    .incbin "cutscene_02_03_bottom.bin"
}
.alloc cutscene_02_04 in text16 {
    .incbin "cutscene_02_04_top.bin"
    .incbin "cutscene_02_04_bottom.bin"
}
.alloc cutscene_02_05 in text16 {
    .incbin "cutscene_02_05_top.bin"
    .incbin "cutscene_02_05_bottom.bin"
}
.alloc cutscene_02_06 in text16 {
    .incbin "cutscene_02_06_top.bin"
    .incbin "cutscene_02_06_bottom.bin"
}
.alloc cutscene_02_07 in text16 {
    .incbin "cutscene_02_07_top.bin"
    .incbin "cutscene_02_07_bottom.bin"
}
.alloc cutscene_02_08 in text16 {
    .incbin "cutscene_02_08_top.bin"
    .incbin "cutscene_02_08_bottom.bin"
}
.alloc cutscene_02_09 in text16 {
    .incbin "cutscene_02_09_top.bin"
    .incbin "cutscene_02_09_bottom.bin"
}
.alloc cutscene_02_10 in text16 {
    .incbin "cutscene_02_10_top.bin"
    .incbin "cutscene_02_10_bottom.bin"
}
.alloc cutscene_02 in cutscene_frames {
    .db 11, 0x2b, 0x03
    .db 1
    .dw -20 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_00
    .db 14
    .db 1
    .dw -4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_01
    .db 24
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_02
    .db 27
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_03
    .db 24
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_04
    .db 21
    .db 1
    .dw 60 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_05
    .db 29
    .db 1
    .dw 76 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_06
    .db 30
    .db 1
    .dw 92 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_07
    .db 14
    .db 1
    .dw 108 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_08
    .db 25
    .db 1
    .dw 124 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_09
    .db 29
    .db 1
    .dw 140 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_02_10
    .db 22
}
.alloc at 0xCC091E size 2 {
    .dw cutscene_02 & 0xFFFF
}
.assert cutscene_02 >> 16 == 0xCC, "cutscene_02: sprite frames are read from bank CC"
.alloc cutscene_03_00 in text16 {
    .incbin "cutscene_03_00_top.bin"
    .incbin "cutscene_03_00_bottom.bin"
}
.alloc cutscene_03_01 in text16 {
    .incbin "cutscene_03_01_top.bin"
    .incbin "cutscene_03_01_bottom.bin"
}
.alloc cutscene_03_02 in text16 {
    .incbin "cutscene_03_02_top.bin"
    .incbin "cutscene_03_02_bottom.bin"
}
.alloc cutscene_03_03 in text16 {
    .incbin "cutscene_03_03_top.bin"
    .incbin "cutscene_03_03_bottom.bin"
}
.alloc cutscene_03_04 in text16 {
    .incbin "cutscene_03_04_top.bin"
    .incbin "cutscene_03_04_bottom.bin"
}
.alloc cutscene_03_05 in text16 {
    .incbin "cutscene_03_05_top.bin"
    .incbin "cutscene_03_05_bottom.bin"
}
.alloc cutscene_03_06 in text16 {
    .incbin "cutscene_03_06_top.bin"
    .incbin "cutscene_03_06_bottom.bin"
}
.alloc cutscene_03_07 in text16 {
    .incbin "cutscene_03_07_top.bin"
    .incbin "cutscene_03_07_bottom.bin"
}
.alloc cutscene_03_08 in text16 {
    .incbin "cutscene_03_08_top.bin"
    .incbin "cutscene_03_08_bottom.bin"
}
.alloc cutscene_03_09 in text16 {
    .incbin "cutscene_03_09_top.bin"
    .incbin "cutscene_03_09_bottom.bin"
}
.alloc cutscene_03_10 in text16 {
    .incbin "cutscene_03_10_top.bin"
    .incbin "cutscene_03_10_bottom.bin"
}
.alloc cutscene_03_11 in text16 {
    .incbin "cutscene_03_11_top.bin"
    .incbin "cutscene_03_11_bottom.bin"
}
.alloc cutscene_03_12 in text16 {
    .incbin "cutscene_03_12_top.bin"
    .incbin "cutscene_03_12_bottom.bin"
}
.alloc cutscene_03_13 in text16 {
    .incbin "cutscene_03_13_top.bin"
    .incbin "cutscene_03_13_bottom.bin"
}
.alloc cutscene_03 in cutscene_frames {
    .db 14, 0x37, 0x03
    .db 1
    .dw 0 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_00
    .db 24
    .db 1
    .dw 16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_01
    .db 25
    .db 1
    .dw 32 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_02
    .db 25
    .db 1
    .dw 48 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_03
    .db 22
    .db 1
    .dw 64 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_04
    .db 27
    .db 1
    .dw 80 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_05
    .db 25
    .db 1
    .dw 96 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_06
    .db 33
    .db 1
    .dw 112 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_07
    .db 27
    .db 1
    .dw 128 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_08
    .db 30
    .db 1
    .dw 144 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_09
    .db 23
    .db 1
    .dw 160 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_10
    .db 29
    .db 1
    .dw 176 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_11
    .db 29
    .db 1
    .dw 192 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_12
    .db 28
    .db 1
    .dw 208 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_03_13
    .db 22
}
.alloc at 0xCC1A37 size 2 {
    .dw cutscene_03 & 0xFFFF
}
.assert cutscene_03 >> 16 == 0xCC, "cutscene_03: sprite frames are read from bank CC"
.alloc cutscene_04_00 in text16 {
    .incbin "cutscene_04_00_top.bin"
    .incbin "cutscene_04_00_bottom.bin"
}
.alloc cutscene_04_01 in text16 {
    .incbin "cutscene_04_01_top.bin"
    .incbin "cutscene_04_01_bottom.bin"
}
.alloc cutscene_04_02 in text16 {
    .incbin "cutscene_04_02_top.bin"
    .incbin "cutscene_04_02_bottom.bin"
}
.alloc cutscene_04_03 in text16 {
    .incbin "cutscene_04_03_top.bin"
    .incbin "cutscene_04_03_bottom.bin"
}
.alloc cutscene_04_04 in text16 {
    .incbin "cutscene_04_04_top.bin"
    .incbin "cutscene_04_04_bottom.bin"
}
.alloc cutscene_04_05 in text16 {
    .incbin "cutscene_04_05_top.bin"
    .incbin "cutscene_04_05_bottom.bin"
}
.alloc cutscene_04_06 in text16 {
    .incbin "cutscene_04_06_top.bin"
    .incbin "cutscene_04_06_bottom.bin"
}
.alloc cutscene_04_07 in text16 {
    .incbin "cutscene_04_07_top.bin"
    .incbin "cutscene_04_07_bottom.bin"
}
.alloc cutscene_04_08 in text16 {
    .incbin "cutscene_04_08_top.bin"
    .incbin "cutscene_04_08_bottom.bin"
}
.alloc cutscene_04_09 in text16 {
    .incbin "cutscene_04_09_top.bin"
    .incbin "cutscene_04_09_bottom.bin"
}
.alloc cutscene_04 in cutscene_frames {
    .db 10, 0x27, 0x03
    .db 1
    .dw -4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_00
    .db 16
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_01
    .db 22
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_02
    .db 25
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_03
    .db 26
    .db 1
    .dw 60 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_04
    .db 26
    .db 1
    .dw 76 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_05
    .db 27
    .db 1
    .dw 92 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_06
    .db 25
    .db 1
    .dw 108 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_07
    .db 27
    .db 1
    .dw 124 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_08
    .db 26
    .db 1
    .dw 140 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_04_09
    .db 16
}
.alloc at 0xCC1A3C size 2 {
    .dw cutscene_04 & 0xFFFF
}
.assert cutscene_04 >> 16 == 0xCC, "cutscene_04: sprite frames are read from bank CC"
.alloc cutscene_05_00 in text16 {
    .incbin "cutscene_05_00_top.bin"
    .incbin "cutscene_05_00_bottom.bin"
}
.alloc cutscene_05_01 in text16 {
    .incbin "cutscene_05_01_top.bin"
    .incbin "cutscene_05_01_bottom.bin"
}
.alloc cutscene_05_02 in text16 {
    .incbin "cutscene_05_02_top.bin"
    .incbin "cutscene_05_02_bottom.bin"
}
.alloc cutscene_05_03 in text16 {
    .incbin "cutscene_05_03_top.bin"
    .incbin "cutscene_05_03_bottom.bin"
}
.alloc cutscene_05 in cutscene_frames {
    .db 4, 0x0f, 0x03
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_05_00
    .db 26
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_05_01
    .db 25
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_05_02
    .db 30
    .db 1
    .dw 60 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_05_03
    .db 21
}
.alloc at 0xCC1A41 size 2 {
    .dw cutscene_05 & 0xFFFF
}
.assert cutscene_05 >> 16 == 0xCC, "cutscene_05: sprite frames are read from bank CC"
.alloc cutscene_06_00 in text16 {
    .incbin "cutscene_06_00_top.bin"
    .incbin "cutscene_06_00_bottom.bin"
}
.alloc cutscene_06_01 in text16 {
    .incbin "cutscene_06_01_top.bin"
    .incbin "cutscene_06_01_bottom.bin"
}
.alloc cutscene_06_02 in text16 {
    .incbin "cutscene_06_02_top.bin"
    .incbin "cutscene_06_02_bottom.bin"
}
.alloc cutscene_06_03 in text16 {
    .incbin "cutscene_06_03_top.bin"
    .incbin "cutscene_06_03_bottom.bin"
}
.alloc cutscene_06_04 in text16 {
    .incbin "cutscene_06_04_top.bin"
    .incbin "cutscene_06_04_bottom.bin"
}
.alloc cutscene_06_05 in text16 {
    .incbin "cutscene_06_05_top.bin"
    .incbin "cutscene_06_05_bottom.bin"
}
.alloc cutscene_06_06 in text16 {
    .incbin "cutscene_06_06_top.bin"
    .incbin "cutscene_06_06_bottom.bin"
}
.alloc cutscene_06_07 in text16 {
    .incbin "cutscene_06_07_top.bin"
    .incbin "cutscene_06_07_bottom.bin"
}
.alloc cutscene_06 in cutscene_frames {
    .db 8, 0x1f, 0x03
    .db 1
    .dw -24 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_00
    .db 27
    .db 1
    .dw -8 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_01
    .db 29
    .db 1
    .dw 8 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_02
    .db 29
    .db 1
    .dw 24 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_03
    .db 25
    .db 1
    .dw 40 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_04
    .db 29
    .db 1
    .dw 56 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_05
    .db 22
    .db 1
    .dw 72 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_06
    .db 32
    .db 1
    .dw 88 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_06_07
    .db 23
}
.alloc at 0xCC2344 size 2 {
    .dw cutscene_06 & 0xFFFF
}
.assert cutscene_06 >> 16 == 0xCC, "cutscene_06: sprite frames are read from bank CC"
.alloc cutscene_07_00 in text16 {
    .incbin "cutscene_07_00_top.bin"
    .incbin "cutscene_07_00_bottom.bin"
}
.alloc cutscene_07_01 in text16 {
    .incbin "cutscene_07_01_top.bin"
    .incbin "cutscene_07_01_bottom.bin"
}
.alloc cutscene_07_02 in text16 {
    .incbin "cutscene_07_02_top.bin"
    .incbin "cutscene_07_02_bottom.bin"
}
.alloc cutscene_07_03 in text16 {
    .incbin "cutscene_07_03_top.bin"
    .incbin "cutscene_07_03_bottom.bin"
}
.alloc cutscene_07_04 in text16 {
    .incbin "cutscene_07_04_top.bin"
    .incbin "cutscene_07_04_bottom.bin"
}
.alloc cutscene_07_05 in text16 {
    .incbin "cutscene_07_05_top.bin"
    .incbin "cutscene_07_05_bottom.bin"
}
.alloc cutscene_07_06 in text16 {
    .incbin "cutscene_07_06_top.bin"
    .incbin "cutscene_07_06_bottom.bin"
}
.alloc cutscene_07_07 in text16 {
    .incbin "cutscene_07_07_top.bin"
    .incbin "cutscene_07_07_bottom.bin"
}
.alloc cutscene_07_08 in text16 {
    .incbin "cutscene_07_08_top.bin"
    .incbin "cutscene_07_08_bottom.bin"
}
.alloc cutscene_07_09 in text16 {
    .incbin "cutscene_07_09_top.bin"
    .incbin "cutscene_07_09_bottom.bin"
}
.alloc cutscene_07 in cutscene_frames {
    .db 10, 0x27, 0x03
    .db 1
    .dw -16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_00
    .db 25
    .db 1
    .dw 0 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_01
    .db 30
    .db 1
    .dw 16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_02
    .db 24
    .db 1
    .dw 32 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_03
    .db 23
    .db 1
    .dw 48 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_04
    .db 27
    .db 1
    .dw 64 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_05
    .db 26
    .db 1
    .dw 80 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_06
    .db 27
    .db 1
    .dw 96 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_07
    .db 26
    .db 1
    .dw 112 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_08
    .db 23
    .db 1
    .dw 128 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_07_09
    .db 18
}
.alloc at 0xCC2349 size 2 {
    .dw cutscene_07 & 0xFFFF
}
.assert cutscene_07 >> 16 == 0xCC, "cutscene_07: sprite frames are read from bank CC"
.alloc cutscene_08_00 in text16 {
    .incbin "cutscene_08_00_top.bin"
    .incbin "cutscene_08_00_bottom.bin"
}
.alloc cutscene_08_01 in text16 {
    .incbin "cutscene_08_01_top.bin"
    .incbin "cutscene_08_01_bottom.bin"
}
.alloc cutscene_08_02 in text16 {
    .incbin "cutscene_08_02_top.bin"
    .incbin "cutscene_08_02_bottom.bin"
}
.alloc cutscene_08_03 in text16 {
    .incbin "cutscene_08_03_top.bin"
    .incbin "cutscene_08_03_bottom.bin"
}
.alloc cutscene_08_04 in text16 {
    .incbin "cutscene_08_04_top.bin"
    .incbin "cutscene_08_04_bottom.bin"
}
.alloc cutscene_08_05 in text16 {
    .incbin "cutscene_08_05_top.bin"
    .incbin "cutscene_08_05_bottom.bin"
}
.alloc cutscene_08_06 in text16 {
    .incbin "cutscene_08_06_top.bin"
    .incbin "cutscene_08_06_bottom.bin"
}
.alloc cutscene_08_07 in text16 {
    .incbin "cutscene_08_07_top.bin"
    .incbin "cutscene_08_07_bottom.bin"
}
.alloc cutscene_08_08 in text16 {
    .incbin "cutscene_08_08_top.bin"
    .incbin "cutscene_08_08_bottom.bin"
}
.alloc cutscene_08_09 in text16 {
    .incbin "cutscene_08_09_top.bin"
    .incbin "cutscene_08_09_bottom.bin"
}
.alloc cutscene_08_10 in text16 {
    .incbin "cutscene_08_10_top.bin"
    .incbin "cutscene_08_10_bottom.bin"
}
.alloc cutscene_08_11 in text16 {
    .incbin "cutscene_08_11_top.bin"
    .incbin "cutscene_08_11_bottom.bin"
}
.alloc cutscene_08 in cutscene_frames {
    .db 12, 0x2f, 0x03
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_00
    .db 23
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_01
    .db 23
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_02
    .db 26
    .db 1
    .dw 60 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_03
    .db 26
    .db 1
    .dw 76 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_04
    .db 25
    .db 1
    .dw 92 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_05
    .db 23
    .db 1
    .dw 108 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_06
    .db 26
    .db 1
    .dw 124 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_07
    .db 30
    .db 1
    .dw 140 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_08
    .db 26
    .db 1
    .dw 156 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_09
    .db 26
    .db 1
    .dw 172 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_10
    .db 26
    .db 1
    .dw 188 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_08_11
    .db 20
}
.alloc at 0xCC234E size 2 {
    .dw cutscene_08 & 0xFFFF
}
.assert cutscene_08 >> 16 == 0xCC, "cutscene_08: sprite frames are read from bank CC"
.alloc cutscene_09_00 in text16 {
    .incbin "cutscene_09_00_top.bin"
    .incbin "cutscene_09_00_bottom.bin"
}
.alloc cutscene_09_01 in text16 {
    .incbin "cutscene_09_01_top.bin"
    .incbin "cutscene_09_01_bottom.bin"
}
.alloc cutscene_09_02 in text16 {
    .incbin "cutscene_09_02_top.bin"
    .incbin "cutscene_09_02_bottom.bin"
}
.alloc cutscene_09_03 in text16 {
    .incbin "cutscene_09_03_top.bin"
    .incbin "cutscene_09_03_bottom.bin"
}
.alloc cutscene_09_04 in text16 {
    .incbin "cutscene_09_04_top.bin"
    .incbin "cutscene_09_04_bottom.bin"
}
.alloc cutscene_09_05 in text16 {
    .incbin "cutscene_09_05_top.bin"
    .incbin "cutscene_09_05_bottom.bin"
}
.alloc cutscene_09_06 in text16 {
    .incbin "cutscene_09_06_top.bin"
    .incbin "cutscene_09_06_bottom.bin"
}
.alloc cutscene_09_07 in text16 {
    .incbin "cutscene_09_07_top.bin"
    .incbin "cutscene_09_07_bottom.bin"
}
.alloc cutscene_09_08 in text16 {
    .incbin "cutscene_09_08_top.bin"
    .incbin "cutscene_09_08_bottom.bin"
}
.alloc cutscene_09_09 in text16 {
    .incbin "cutscene_09_09_top.bin"
    .incbin "cutscene_09_09_bottom.bin"
}
.alloc cutscene_09 in cutscene_frames {
    .db 10, 0x27, 0x03
    .db 1
    .dw -16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_00
    .db 32
    .db 1
    .dw 0 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_01
    .db 32
    .db 1
    .dw 16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_02
    .db 23
    .db 1
    .dw 32 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_03
    .db 24
    .db 1
    .dw 48 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_04
    .db 27
    .db 1
    .dw 64 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_05
    .db 30
    .db 1
    .dw 80 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_06
    .db 28
    .db 1
    .dw 96 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_07
    .db 26
    .db 1
    .dw 112 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_08
    .db 31
    .db 1
    .dw 128 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_09_09
    .db 21
}
.alloc at 0xCC2353 size 2 {
    .dw cutscene_09 & 0xFFFF
}
.assert cutscene_09 >> 16 == 0xCC, "cutscene_09: sprite frames are read from bank CC"
.alloc cutscene_10_00 in text16 {
    .incbin "cutscene_10_00_top.bin"
    .incbin "cutscene_10_00_bottom.bin"
}
.alloc cutscene_10_01 in text16 {
    .incbin "cutscene_10_01_top.bin"
    .incbin "cutscene_10_01_bottom.bin"
}
.alloc cutscene_10_02 in text16 {
    .incbin "cutscene_10_02_top.bin"
    .incbin "cutscene_10_02_bottom.bin"
}
.alloc cutscene_10_03 in text16 {
    .incbin "cutscene_10_03_top.bin"
    .incbin "cutscene_10_03_bottom.bin"
}
.alloc cutscene_10_04 in text16 {
    .incbin "cutscene_10_04_top.bin"
    .incbin "cutscene_10_04_bottom.bin"
}
.alloc cutscene_10_05 in text16 {
    .incbin "cutscene_10_05_top.bin"
    .incbin "cutscene_10_05_bottom.bin"
}
.alloc cutscene_10_06 in text16 {
    .incbin "cutscene_10_06_top.bin"
    .incbin "cutscene_10_06_bottom.bin"
}
.alloc cutscene_10_07 in text16 {
    .incbin "cutscene_10_07_top.bin"
    .incbin "cutscene_10_07_bottom.bin"
}
.alloc cutscene_10_08 in text16 {
    .incbin "cutscene_10_08_top.bin"
    .incbin "cutscene_10_08_bottom.bin"
}
.alloc cutscene_10_09 in text16 {
    .incbin "cutscene_10_09_top.bin"
    .incbin "cutscene_10_09_bottom.bin"
}
.alloc cutscene_10_10 in text16 {
    .incbin "cutscene_10_10_top.bin"
    .incbin "cutscene_10_10_bottom.bin"
}
.alloc cutscene_10 in cutscene_frames {
    .db 11, 0x2b, 0x03
    .db 1
    .dw 4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_00
    .db 23
    .db 1
    .dw 20 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_01
    .db 21
    .db 1
    .dw 36 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_02
    .db 27
    .db 1
    .dw 52 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_03
    .db 22
    .db 1
    .dw 68 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_04
    .db 23
    .db 1
    .dw 84 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_05
    .db 29
    .db 1
    .dw 100 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_06
    .db 23
    .db 1
    .dw 116 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_07
    .db 23
    .db 1
    .dw 132 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_08
    .db 26
    .db 1
    .dw 148 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_09
    .db 30
    .db 1
    .dw 164 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_10_10
    .db 22
}
.alloc at 0xCC2358 size 2 {
    .dw cutscene_10 & 0xFFFF
}
.assert cutscene_10 >> 16 == 0xCC, "cutscene_10: sprite frames are read from bank CC"
.alloc cutscene_11_00 in text16 {
    .incbin "cutscene_11_00_top.bin"
    .incbin "cutscene_11_00_bottom.bin"
}
.alloc cutscene_11_01 in text16 {
    .incbin "cutscene_11_01_top.bin"
    .incbin "cutscene_11_01_bottom.bin"
}
.alloc cutscene_11_02 in text16 {
    .incbin "cutscene_11_02_top.bin"
    .incbin "cutscene_11_02_bottom.bin"
}
.alloc cutscene_11_03 in text16 {
    .incbin "cutscene_11_03_top.bin"
    .incbin "cutscene_11_03_bottom.bin"
}
.alloc cutscene_11_04 in text16 {
    .incbin "cutscene_11_04_top.bin"
    .incbin "cutscene_11_04_bottom.bin"
}
.alloc cutscene_11_05 in text16 {
    .incbin "cutscene_11_05_top.bin"
    .incbin "cutscene_11_05_bottom.bin"
}
.alloc cutscene_11_06 in text16 {
    .incbin "cutscene_11_06_top.bin"
    .incbin "cutscene_11_06_bottom.bin"
}
.alloc cutscene_11_07 in text16 {
    .incbin "cutscene_11_07_top.bin"
    .incbin "cutscene_11_07_bottom.bin"
}
.alloc cutscene_11_08 in text16 {
    .incbin "cutscene_11_08_top.bin"
    .incbin "cutscene_11_08_bottom.bin"
}
.alloc cutscene_11_09 in text16 {
    .incbin "cutscene_11_09_top.bin"
    .incbin "cutscene_11_09_bottom.bin"
}
.alloc cutscene_11 in cutscene_frames {
    .db 10, 0x27, 0x03
    .db 1
    .dw -28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_00
    .db 24
    .db 1
    .dw -12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_01
    .db 27
    .db 1
    .dw 4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_02
    .db 23
    .db 1
    .dw 20 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_03
    .db 29
    .db 1
    .dw 36 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_04
    .db 23
    .db 1
    .dw 52 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_05
    .db 30
    .db 1
    .dw 68 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_06
    .db 22
    .db 1
    .dw 84 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_07
    .db 27
    .db 1
    .dw 100 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_08
    .db 24
    .db 1
    .dw 116 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_11_09
    .db 28
}
.alloc at 0xCC235D size 2 {
    .dw cutscene_11 & 0xFFFF
}
.assert cutscene_11 >> 16 == 0xCC, "cutscene_11: sprite frames are read from bank CC"
.alloc cutscene_12_00 in text16 {
    .incbin "cutscene_12_00_top.bin"
    .incbin "cutscene_12_00_bottom.bin"
}
.alloc cutscene_12_01 in text16 {
    .incbin "cutscene_12_01_top.bin"
    .incbin "cutscene_12_01_bottom.bin"
}
.alloc cutscene_12_02 in text16 {
    .incbin "cutscene_12_02_top.bin"
    .incbin "cutscene_12_02_bottom.bin"
}
.alloc cutscene_12_03 in text16 {
    .incbin "cutscene_12_03_top.bin"
    .incbin "cutscene_12_03_bottom.bin"
}
.alloc cutscene_12_04 in text16 {
    .incbin "cutscene_12_04_top.bin"
    .incbin "cutscene_12_04_bottom.bin"
}
.alloc cutscene_12_05 in text16 {
    .incbin "cutscene_12_05_top.bin"
    .incbin "cutscene_12_05_bottom.bin"
}
.alloc cutscene_12_06 in text16 {
    .incbin "cutscene_12_06_top.bin"
    .incbin "cutscene_12_06_bottom.bin"
}
.alloc cutscene_12_07 in text16 {
    .incbin "cutscene_12_07_top.bin"
    .incbin "cutscene_12_07_bottom.bin"
}
.alloc cutscene_12_08 in text16 {
    .incbin "cutscene_12_08_top.bin"
    .incbin "cutscene_12_08_bottom.bin"
}
.alloc cutscene_12 in cutscene_frames {
    .db 9, 0x23, 0x03
    .db 1
    .dw -4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_00
    .db 18
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_01
    .db 27
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_02
    .db 26
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_03
    .db 25
    .db 1
    .dw 60 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_04
    .db 25
    .db 1
    .dw 76 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_05
    .db 31
    .db 1
    .dw 92 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_06
    .db 26
    .db 1
    .dw 108 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_07
    .db 25
    .db 1
    .dw 124 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_12_08
    .db 10
}
.alloc at 0xCC2362 size 2 {
    .dw cutscene_12 & 0xFFFF
}
.assert cutscene_12 >> 16 == 0xCC, "cutscene_12: sprite frames are read from bank CC"
.alloc cutscene_13_00 in text16 {
    .incbin "cutscene_13_00_top.bin"
    .incbin "cutscene_13_00_bottom.bin"
}
.alloc cutscene_13_01 in text16 {
    .incbin "cutscene_13_01_top.bin"
    .incbin "cutscene_13_01_bottom.bin"
}
.alloc cutscene_13_02 in text16 {
    .incbin "cutscene_13_02_top.bin"
    .incbin "cutscene_13_02_bottom.bin"
}
.alloc cutscene_13_03 in text16 {
    .incbin "cutscene_13_03_top.bin"
    .incbin "cutscene_13_03_bottom.bin"
}
.alloc cutscene_13 in cutscene_frames {
    .db 4, 0x0f, 0x03
    .db 1
    .dw -4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_13_00
    .db 25
    .db 1
    .dw 12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_13_01
    .db 25
    .db 1
    .dw 28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_13_02
    .db 26
    .db 1
    .dw 44 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_13_03
    .db 20
}
.alloc at 0xCC2367 size 2 {
    .dw cutscene_13 & 0xFFFF
}
.assert cutscene_13 >> 16 == 0xCC, "cutscene_13: sprite frames are read from bank CC"
.alloc cutscene_14_00 in text16 {
    .incbin "cutscene_14_00_top.bin"
    .incbin "cutscene_14_00_bottom.bin"
}
.alloc cutscene_14_01 in text16 {
    .incbin "cutscene_14_01_top.bin"
    .incbin "cutscene_14_01_bottom.bin"
}
.alloc cutscene_14_02 in text16 {
    .incbin "cutscene_14_02_top.bin"
    .incbin "cutscene_14_02_bottom.bin"
}
.alloc cutscene_14_03 in text16 {
    .incbin "cutscene_14_03_top.bin"
    .incbin "cutscene_14_03_bottom.bin"
}
.alloc cutscene_14_04 in text16 {
    .incbin "cutscene_14_04_top.bin"
    .incbin "cutscene_14_04_bottom.bin"
}
.alloc cutscene_14_05 in text16 {
    .incbin "cutscene_14_05_top.bin"
    .incbin "cutscene_14_05_bottom.bin"
}
.alloc cutscene_14_06 in text16 {
    .incbin "cutscene_14_06_top.bin"
    .incbin "cutscene_14_06_bottom.bin"
}
.alloc cutscene_14_07 in text16 {
    .incbin "cutscene_14_07_top.bin"
    .incbin "cutscene_14_07_bottom.bin"
}
.alloc cutscene_14_08 in text16 {
    .incbin "cutscene_14_08_top.bin"
    .incbin "cutscene_14_08_bottom.bin"
}
.alloc cutscene_14_09 in text16 {
    .incbin "cutscene_14_09_top.bin"
    .incbin "cutscene_14_09_bottom.bin"
}
.alloc cutscene_14_10 in text16 {
    .incbin "cutscene_14_10_top.bin"
    .incbin "cutscene_14_10_bottom.bin"
}
.alloc cutscene_14_11 in text16 {
    .incbin "cutscene_14_11_top.bin"
    .incbin "cutscene_14_11_bottom.bin"
}
.alloc cutscene_14 in cutscene_frames {
    .db 12, 0x2f, 0x03
    .db 1
    .dw -28 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_00
    .db 16
    .db 1
    .dw -12 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_01
    .db 27
    .db 1
    .dw 4 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_02
    .db 25
    .db 1
    .dw 20 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_03
    .db 24
    .db 1
    .dw 36 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_04
    .db 27
    .db 1
    .dw 52 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_05
    .db 22
    .db 1
    .dw 68 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_06
    .db 27
    .db 1
    .dw 84 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_07
    .db 28
    .db 1
    .dw 100 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_08
    .db 27
    .db 1
    .dw 116 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_09
    .db 31
    .db 1
    .dw 132 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_10
    .db 26
    .db 1
    .dw 148 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_14_11
    .db 18
}
.alloc at 0xCC236C size 2 {
    .dw cutscene_14 & 0xFFFF
}
.assert cutscene_14 >> 16 == 0xCC, "cutscene_14: sprite frames are read from bank CC"
.alloc cutscene_15_00 in text16 {
    .incbin "cutscene_15_00_top.bin"
    .incbin "cutscene_15_00_bottom.bin"
}
.alloc cutscene_15_01 in text16 {
    .incbin "cutscene_15_01_top.bin"
    .incbin "cutscene_15_01_bottom.bin"
}
.alloc cutscene_15_02 in text16 {
    .incbin "cutscene_15_02_top.bin"
    .incbin "cutscene_15_02_bottom.bin"
}
.alloc cutscene_15_03 in text16 {
    .incbin "cutscene_15_03_top.bin"
    .incbin "cutscene_15_03_bottom.bin"
}
.alloc cutscene_15 in cutscene_frames {
    .db 4, 0x0f, 0x03
    .db 1
    .dw 0 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_15_00
    .db 16
    .db 1
    .dw 16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_15_01
    .db 15
    .db 1
    .dw 32 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_15_02
    .db 14
    .db 1
    .dw 48 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_15_03
    .db 11
}
.alloc at 0xCC2371 size 2 {
    .dw cutscene_15 & 0xFFFF
}
.assert cutscene_15 >> 16 == 0xCC, "cutscene_15: sprite frames are read from bank CC"
.alloc cutscene_16_00 in text16 {
    .incbin "cutscene_16_00_top.bin"
    .incbin "cutscene_16_00_bottom.bin"
}
.alloc cutscene_16_01 in text16 {
    .incbin "cutscene_16_01_top.bin"
    .incbin "cutscene_16_01_bottom.bin"
}
.alloc cutscene_16_02 in text16 {
    .incbin "cutscene_16_02_top.bin"
    .incbin "cutscene_16_02_bottom.bin"
}
.alloc cutscene_16 in cutscene_frames {
    .db 3, 0x0b, 0x03
    .db 1
    .dw -8 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_16_00
    .db 17
    .db 1
    .dw 8 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_16_01
    .db 15
    .db 1
    .dw 24 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_16_02
    .db 12
}
.alloc at 0xCC2376 size 2 {
    .dw cutscene_16 & 0xFFFF
}
.assert cutscene_16 >> 16 == 0xCC, "cutscene_16: sprite frames are read from bank CC"
.alloc cutscene_17_00 in text16 {
    .incbin "cutscene_17_00_top.bin"
    .incbin "cutscene_17_00_bottom.bin"
}
.alloc cutscene_17_01 in text16 {
    .incbin "cutscene_17_01_top.bin"
    .incbin "cutscene_17_01_bottom.bin"
}
.alloc cutscene_17_02 in text16 {
    .incbin "cutscene_17_02_top.bin"
    .incbin "cutscene_17_02_bottom.bin"
}
.alloc cutscene_17_03 in text16 {
    .incbin "cutscene_17_03_top.bin"
    .incbin "cutscene_17_03_bottom.bin"
}
.alloc cutscene_17 in cutscene_frames {
    .db 4, 0x0f, 0x03
    .db 1
    .dw 0 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_17_00
    .db 17
    .db 1
    .dw 16 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_17_01
    .db 16
    .db 1
    .dw 32 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_17_02
    .db 15
    .db 1
    .dw 48 & 0xFFFF, 0 & 0xFFFF
    .dl cutscene_17_03
    .db 9
}
.alloc at 0xCC237B size 2 {
    .dw cutscene_17 & 0xFFFF
}
.assert cutscene_17 >> 16 == 0xCC, "cutscene_17: sprite frames are read from bank CC"
.alloc credit_title_0 in text16 {
    .incbin "credit_title_0.bin"
}
.alloc at 0xC2DA5A size 3 {
    .dl credit_title_0
}
.alloc at 0xC2DA6A size 3 {
    .dl credit_title_0
}
.alloc credit_title_1 in text16 {
    .incbin "credit_title_1.bin"
}
.alloc at 0xC2DA7A size 3 {
    .dl credit_title_1
}
.alloc credit_title_2 in text16 {
    .incbin "credit_title_2.bin"
}
.alloc at 0xC2DA8B size 3 {
    .dl credit_title_2
}
.alloc credit_title_3 in text16 {
    .incbin "credit_title_3.bin"
}
.alloc at 0xC2DA9B size 3 {
    .dl credit_title_3
}
.alloc credit_title_4 in text16 {
    .incbin "credit_title_4.bin"
}
.alloc at 0xC2DAAB size 3 {
    .dl credit_title_4
}
.alloc at 0xC2DABB size 3 {
    .dl credit_title_4
}
.alloc at 0xC2DACC size 3 {
    .dl credit_title_4
}
