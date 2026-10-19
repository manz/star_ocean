# Script stream

- Scene script unpacked at scene load (see `compression/lz_container.md`), e.g. `E8:41FC` → `$7E:B873`.
  Strings sit inside the scene's event data; a higher VM layer handles its own opcodes
  (`01 FF FF 02 xx 53 …` patterns) before text reaches the text engine.
- Read cursor `$03D5` (bank 7E), rewind target `$03D7`, flags `$03D2`.
- `C2:39DB` fetch: `FFFF` end, `FFFE` rewind; low byte bit7 → 2-byte code `(lo & 0x7F) | hi << 7`.
- `C2:3A4D` dispatch: `0-3` control, `>= 0x140` → `C2:68EE` (TBD), else **glyph = code − 5**.
- TODO: name codes, the VM opcodes, a glyph→char table for dumping.
