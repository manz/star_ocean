# 8x8 VWF budget

- Dialog: framebuffer is a bitmap → **no VRAM change**. New blitter writes 8-row glyphs at any y
  (rows linear inside a cell). 208×64 px window: 8 lines @ 8 px, or 6 @ 10, or 5 @ 12.
- Menu: pooled tiles already (old patch: glyphs copied to a `$7F` buffer, tile ids from `0x114`).
  BG4 2bpp window has ~420 free tiles for an 8×8 pool.
