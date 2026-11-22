# Runtime 8x8 pen (VWF8_PEN, src/menu/pen8.s)

Names typed in game have no baked record: vwf8's `_find` misses, then `pen8_find` draws the string with katsuji's
`sumi/8` (glyph rows and advances baked by tools/pen8.py) and serves it as a vwf8 record.

- Sources: bank `$7E`, the party records (`$1548-$15D7`, name then nickname) or the fight's party names
  (`$7E:7497 + n * $100`, 4 codes and `FF`). Anything else stays with the caller.
- Cache: 12 SRAM slots keyed by the codes (up to 6), round robin. A name is drawn once, then found by every later
  draw, across fights, menus and resets. `PEN8_MAGIC` (crc of the glyph tables) drops a cache another font left.
- Drawing: ink advances by its width plus 1 pixel, the space by 3, then the menu font's shadow (right, down,
  diagonal) as colour 1, ink colour 3. Tiles = ceil(pen x / 8), refused past the name's code count.
- Upload: the record's tiles are plain 2bpp in SRAM; the queue slot's byte 7 = 1 sends them with a plain DMA
  (mode 1), not through the S-DD1. The vwf8 record id is `VWF8_RECORDS + slot`; a redrawn slot clears its home.
- SRAM: 1.6 KB. `sram_text` went from 20 KB to 18 KB to make room (the largest French scene block is 13.1 KB);
  about 700 bytes of the `sram` pool stay free.
- The field menus do not draw names through this path yet (no golden changed): they print them elsewhere.
