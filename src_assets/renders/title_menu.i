.alloc title_menu_0 in cutscene_frames {
    .db 0x87, 0x00, 0x00
    .db 1
    .dw 0, 0
    .dw 0x018E
    .db 1
    .dw 16, 0
    .dw 0x01A0
    .db 1
    .dw 32, 0
    .dw 0x01A2
    .db 1
    .dw 48, 0
    .dw 0x01A4
    .db 1
    .dw 64, 0
    .dw 0x01A6
    .db 1
    .dw 80, 0
    .dw 0x01A8
    .db 1
    .dw 96, 0
    .dw 0x01AA
}
.alloc at 0xCC2BD0 size 2 {
    .dw title_menu_0 & 0xFFFF
}
.assert title_menu_0 >> 16 == 0xCC, "title_menu_0: sprite frames are read from bank CC"
.alloc title_menu_1 in cutscene_frames {
    .db 0x85, 0x00, 0x00
    .db 1
    .dw 0, 0
    .dw 0x01AC
    .db 1
    .dw 16, 0
    .dw 0x01AE
    .db 1
    .dw 32, 0
    .dw 0x01C0
    .db 1
    .dw 48, 0
    .dw 0x01C2
    .db 1
    .dw 64, 0
    .dw 0x01C4
}
.alloc at 0xCC2BFB size 2 {
    .dw title_menu_1 & 0xFFFF
}
.assert title_menu_1 >> 16 == 0xCC, "title_menu_1: sprite frames are read from bank CC"
.alloc title_menu_2 in cutscene_frames {
    .db 0x85, 0x00, 0x00
    .db 1
    .dw 0, 0
    .dw 0x01C6
    .db 1
    .dw 16, 0
    .dw 0x01C8
    .db 1
    .dw 32, 0
    .dw 0x01CA
    .db 1
    .dw 48, 0
    .dw 0x01CC
    .db 1
    .dw 64, 0
    .dw 0x01CE
}
.alloc at 0xCC2C1F size 2 {
    .dw title_menu_2 & 0xFFFF
}
.assert title_menu_2 >> 16 == 0xCC, "title_menu_2: sprite frames are read from bank CC"
.alloc title_sheet in text16 {
    .incbin "title_sheet.bin"
}
.alloc at 0xCC2442 size 2 {
    .dw title_sheet & 0xFFFF
}
.alloc at 0xCC2448 size 1 {
    .db title_sheet >> 16
}
