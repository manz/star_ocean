"""
French 8x8 menu font (fonts/so_menu8.png, tools/menu_font.py) in place of the game's: same S-DD1 stream address,
so the five loaders (C0:239B, C0:83B4, C5:01DC, CA:64CD, CA:6832) stay as they are.
"""

.alloc menu_font8 at 0xDBA078 size 1954 {
    .incbin "menu_font8.bin"
}
