# Game fonts

| font | source | format | used by |
|---|---|---|---|
| dialog 16×16 | `FF:0000` uncompressed | 1bpp, 32 B/glyph (left col 16 B, right col 16 B), ≤ 0x640 glyphs | dialog framebuffer, name entry |
| menu 8×8 | S-DD1 `DB:A078`, 0xC00 B | 2bpp tiles → VRAM `$2000` (`CA:64EE`) | menu commands / labels |

Menu 8×8 tile order: ASCII 0x20-0x5F, then katakana, hiragana, ★ ○ ×.
Dump: `uv run python -m tools.dump_font` → `extracted/fonts/`.
