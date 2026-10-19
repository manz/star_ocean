"""
French 16x16 font, the dialog font's glyphs (tools/menu_font16.py) in place of the kanji at FF:0000, same 1bpp
layout, so `C8:0C3C` blits it as it is. The widths feed the VWF (src/menu/vwf16.s).
"""

.import "core/preamble"

.alloc menu_font16 at 0xFF0000 {
    .incbin "menu_font16.bin"
}
.assert sizeof(menu_font16) <= 0x1800, "16x16 font overruns the text16 pool at FF:1800"

.alloc menu_font16_widths in code_c8 {
    .incbin "menu_font16_widths.bin"
}
