# Text framebuffer

- WRAM `$7E:A353`, 2bpp, mirrored to VRAM `$5940` = BG3 tiles `0x328-0x3F7` (chr base `$4000`).
- 4 lines × 26 cells of 16 px. Each cell = top/bottom tile pair = 32 contiguous bytes
  (one 8 px column, 16 rows). Next cell row = +26×32 B.
- BG3 map `$5800`, only rows 0-9 used (`$5800-$593F`), CHR packed right after. Shown via BG3 VOFS −145.
- Intro narration reuses `$5940` with pre-rendered S-DD1 bitmaps (`C2:E07E`).
