# Dialog / menu font `FF:0000`

- ROM `0x3F0000`, uncompressed, 16×16 1bpp, 32 B per glyph: left 8 px column (16 rows) then right.
- ≤ 0x640 glyphs (`FF:C800` is an LZ blob).
- 0 = space, 1-10 = 0-9, then hiragana, katakana, Latin A-Z around `0xE4`, kanji after.

See `fonts/game_fonts.md` for the menu 8×8 font.
