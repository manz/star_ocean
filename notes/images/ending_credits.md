# Ending staff roll

Map 605, after story 177 (the credits, then the epilogue on map 589). Not images: text drawn at run time.

- `C0:66B0`: S-DD1 DMA of the font sheet `DC:698A` (0xE00 bytes, 2bpp, 16 tiles wide) to `$7F:0000`.
- `C0:66EC`: `ldy #$D8F0 / lda #$DE / jsl C0:4C53`, the roll's container (0x83 LZSS, 175 lines) to `$7F:4000`.
- `C0:6740`: every 0x40 frames, one line measured (`C0:693E`), drawn (`C0:6815`) into `$7E:D073` and DMA'd to VRAM.
- Line: count byte, ASCII, 0. The count is how many characters are measured: x = 0x70 - (width + 4), the role
  right-aligned to the names at x = 0x70. Bit 7 halves the width: 255 centres the line on x = 0x6C, not the
  screen. 1 + two spaces: a name under the one above. 0: blank. 254: the end.
- `C0:6996`: ASCII 0x20-0x7A → glyph (`# $ % * + < > @ [ \ ] ^ _ \`` are unused duplicates). `C0:69F1`: 0x4D
  records (advance, rows, columns, first tile word), followed by the `code_c0` pool. No accented letters.

French: `text/fr/ending_credits.toml` → `tools/ending_credits.py` (é è à ç É drawn from their base letters into
free tile pairs, on spare codes, the record table copied with them) → `src/dialog/ending_credits.s`.
