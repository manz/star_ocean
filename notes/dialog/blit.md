# Glyph blit `C2:63A0`

Entry M=0 X=0, `A` = glyph.
1. Source `FF:(glyph * 32)`, copied to DP `$0331..` (DP = `$0300`).
2. Shifted right by `$D9 & 7` (sub-tile x) through `$31,x → $41,x → $51,x` (24 px wide).
3. Composed 1bpp → 2bpp per `$03DE` (0..3: or / and-not / xor style variants).
4. Merged into the framebuffer (writes at `C2:656E/6577/6580`).

Already pixel-positioned, so a proportional font only needs widths + an x advance.
