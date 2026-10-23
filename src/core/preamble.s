"""
Build context every module imports: free ROM, cart SRAM layout. The bus map lives in a816.toml.
"""

; Bank $C0 padding before $C0:7000 (power-on MMC page 0, always mapped).
.pool code_c0 {
    range 0xC06B72 0xC06FFF
    strategy order
}

; Bank $C1 padding: battle loop code reached with `jsr` from its own bank (src/engine).
.pool code_c1 {
    range 0xC1FF4D 0xC1FFFF
    strategy order
}

; Bank $C3 padding: trampolines for battle code that calls into the sprite pipeline (src/engine).
.pool code_c3 {
    range 0xC3FFAD 0xC3FFFF
    strategy order
}

; Bank $C5 padding: battle code reached by `jml` (src/engine).
.pool code_c5 {
    range 0xC5FF3A 0xC5FFFF
    strategy order
}

; Bank padding the menu code can reach with `jsr` from its own bank.
.pool code_c6 {
    range 0xC6FE63 0xC6FFFF
    strategy order
}
.pool code_c8 {
    range 0xC8FAA7 0xC8FFFF
    strategy order
}

; Bank $C4 padding: code reached by `jml` / `jsl` and data read long.
.pool code_c4 {
    range 0xC4FB26 0xC4FFFF
    strategy order
}

; Cart SRAM once the header says 32 KB: the saves sit at $70:0000-1E6A (core/saves moves them there), the rest is ours.
.pool sram {
    bss
    range 0x702000 0x707FFF
    strategy order
}

; ROM pages 6-7 behind pseudo-banks $40-$5F (a816.toml [map.1]): data only, read with the E window switched.
.pool rom_pages_67 {
    range 0x400000 0x5FFFFE
    strategy pack
}
