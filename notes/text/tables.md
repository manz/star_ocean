# Character tables

## `text/so_dialog.tbl`: 16×16 font (`FF:0000`)
Keys are stream bytes (glyph + 5, varint-encoded: `05`…`7F`, then `80 01`…). The same glyph index serves
the 16×16 menu strings with base 0x10 instead of 5.

Order: blank, digits, hiragana, katakana (dakuten forms interleaved), small kana, fullwidth A–Z, then
~1390 kanji/symbols in game-frequency order. Not JIS.

Transcribed by eye with a template-matching OCR (system fonts, JIS X 0208 kanji) as a hint, then:
duplicates resolved by strokes or by script context (e.g. 聞/闇, 怠/急, 脅/昔, 謁/踊, 極/擾, 0x499 = ×).
Low-frequency kanji past ~0x4C0 are the least certain. `[g4B6]`, `[g5B3]` are unused glyphs left
unidentified; `0x239` drawn as `―`. Visually identical pairs split by group: べ/ベ, ぺ/ペ.

Re-check a glyph: `extracted/fonts/dialog_16x16.png` (16 per row).

## `text/so_dialog_ctl.tbl`: dialog controls
`[page]` (keeps the line break after it in the XML), `\n`, `[end]` (FFFF), `[rewind]` (FFFE); arguments
follow as `[0xNN]`. `02 NN` name inserts with the default party names as tags: `[nick:ラティ]` (00-0B),
`[name:ラティクス]` (0C-17); other slots stay `[str][0xNN]` (≥ 0x18 = first letter only, C2:3EE3).
The buffers are runtime WRAM (`C2:3F21` → `$15xx`), 8×8-encoded.

## 16×16 menu table
Derived at dump time into `build/gen/so_menu16.tbl` (u16 LE glyph + 0x10, `0D00` newline, `FFFF` end).

## `text/so_menu.tbl`: 8×8 font (`DB:A078`)
Tile order ≈ ASCII 0x20-0x5F then JIS X 0201 kana, then hiragana. `C0-F2` = voiced codes (see `strings.md`).
