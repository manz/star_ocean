"""
Build context every module imports: free ROM, cart SRAM layout. The bus map lives in a816.toml.
"""

; Bank $C0 padding before $C0:7000 (power-on MMC page 0, always mapped).
.pool code_c0 {
    range 0xC06B72 0xC06FFF
    strategy order
}

; Cart SRAM once the header says 32 KB: the game keeps its saves at $70:6000-$7E67, below is ours.
.pool sram {
    bss
    range 0x700000 0x705FFF
    strategy order
}

; ROM pages 6-7 behind pseudo-banks $40-$5F (a816.toml [map.1]): data only, read with the E window switched.
.pool rom_pages_67 {
    range 0x400000 0x5FFFFE
    strategy pack
}
