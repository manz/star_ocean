# 8x8 VWF budget

- Dialog: framebuffer is a bitmap → **no VRAM change**. New blitter writes 8-row glyphs at any y
  (rows linear inside a cell). 208×64 px window: 8 lines @ 8 px, or 6 @ 10, or 5 @ 12.
- Menu: pooled tiles already (old patch: glyphs copied to a `$7F` buffer, tile ids from `0x114`).
  BG4 2bpp window has ~420 free tiles for an 8×8 pool.

## Todo: a dynamic 8x8 VWF

The menu 8x8 VWF (`src/menu/vwf8.s`) only draws strings `tools/vwf8.py` baked at build time. Baking every string
the game prints doesn't scale: menu16 help lines (shop help, `C6:F6F9` by id from `CA:BB02`), item and skill
descriptions (`C6:F7D1` u16 buffer) stay on the 16x16 VWF until an 8x8 VWF renders glyphs at run time into the
pool, like `src/menu/vwf16.s` does for the big font.
