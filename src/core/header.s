"""
Cart header and image size: SRAM 8 KB -> 32 KB, so $70:0000-$5FFF stops mirroring the saves at $70:6000;
the ROM image runs to 8 MB (header ROM size $0D already says so).
"""

.alloc at 0xC07FD8 size 1 {
    .db 0x05
}

; The last byte of page 7, so an IPS-patched image is 8 MB long.
.alloc at 0x5FFFFF size 1 {
    .db 0xFF
}
