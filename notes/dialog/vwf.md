# Dialog VWF (patch: src/dialog/vwf.s)

- Font: katsuji's builtin `sumi/16` (8x16, FF4's VWF font) on `text/so_fr.tbl` (cell index = stream code,
  `katsuji.toml` `[fonts.dialog]`).
  `05` space, `06-0F` digits (numbers print as digit + 1, Japanese layout kept), `10-29` A-Z, `2A-43` a-z,
  accents, punctuation, ○★☆♀♂♥♪; 112 glyphs, all one byte (< `$80`).
- Data: codes `00-7F` of the katsuji record file (17 B each: 16 rows + width) at `FF:BF80-C7FF`, over 16x16
  glyphs `0x5FC-0x63F` (the blit reads `FF:` with the F window on page 3). 46 uses of those kanji in the
  Japanese 16x16 menus garble until menus are French.
- `C2:63B4`: the 16-word copy from `FF:(glyph*32)` -> `dialog_glyph_load` (rows into the left column
  `$0331-$0340` shifted 1 px right, `$0341-$0360` cleared, width to `dialog_advance` in SRAM), then `jmp $6414`.
  The shadow (`C2:65CD`: glyph << 1 | glyph >> 1) drops a left pixel past the tile-aligned 24 px window: a glyph
  inked in column 0 at `$D9 & 7 == 0` lost its left shade.
- `C2:65B9`: `lda $D9 / clc / adc #$0C / adc $DB / sta $D9` -> pen += width + 1 + spacing.

# ROM pages 6-7 (8 MB)

The S-DD1 windows: `$4804`/`$4805` (C, D) never change (pages 0, 1); `$4806`/`$4807` (E, F) are 2/3 in main
code, and the interrupt handler at `C0:0388` saves them, sets 4/5 and restores. So main code may switch the E
window itself. The patch addresses pages 6-7 as pseudo-banks `$40-$5F` (`a816.toml [map.1]`, base `0x600000`);
`text_unpack_sram` maps a pseudo-bank to `$4806` = 6/7 + bank `$E0-$EF`, restores `$4806` at the end. The image
is padded to 8 MB (`core/header.s`); the header's ROM size byte is already `$0D`.

French scene blocks (`tools/encode_text.py`, 177.5 KB packed) live there; the scene table's text pointers
(`E4:0000 + 6n + 3`) point at them. Scene 2 (test message) keeps its Japanese block.

# Lines, names, layout

- Window: 4 lines; a fuller page prompts, then scrolls (native). Width: the dispatcher peeks for a break once the
  pen passes `$C5` (196 px).
- `$03DF` counts glyphs down per line; the measure at `C2:4134` set it to 17 (Japanese window). Patched to 0xFF at
  `C2:416A`: only a newline or page ends a line. `C2:4122` set letter spacing `$03DB` = 1 on short lines: now 0.
- Name inserts (`text_insert_string` `C2:3EE3`, ids 00-17): the game converts the 8x8 name record at
  `$7E:1548 + 12 n` (slots `C2:3F21`) through `C0:4B60`, as in the Japanese, so an entered name shows. Records:
  name (6 codes) + `FF`, nickname (4) + `FF`; `[nick:]` reads Ratix's nickname but the others' name. New game
  `C2:D85C` and save load `C2:D6E7` are hooked (`src/dialog/names.s`, `tools/party_names.py`): French defaults,
  and older saves' default names (kana, DeJap English, earlier French) replaced.
- `tools/reflow.py`: katsuji reflow of each page at build time; speaker label line kept; name tags measured as the
  French name. `tests/test_hooks.py` pins the base bytes under every hook.
