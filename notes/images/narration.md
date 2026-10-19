# Narration line images

Pre-rendered text, not font text. Shown by the text VM (`C2:38AB → C2:56AA → C2:6791`).

- Table `C2:681A`: 13 screens × 16 B = four 3-byte S-DD1 line pointers (`E3:FFF7` = blank line),
  a 3-byte palette pointer (colours 1-3 at +2/+4/+6 → `$03E0-$03E5`), one pad byte.
- Screen `$03E6`, line `$0490` → VRAM `$5940/$5AE0/$5C80/$5E20` (the dialog framebuffer rows).
- Each line: 0x340 B = 26 cells × (top + bottom 2bpp tile) = 208×16.
- Screen 0 is the Kurt village chief's letter (parchment palette `FE:FDFB`); 1-12 are the Calnus intro
  lines (palette `FE:FE03`).
- Dump: `uv run python -m tools.dump_images` → `extracted/images/narration/`.
- Patch path: re-render 208×16 lines, S-DD1-compress or (simpler) hook `C2:6791` to DMA uncompressed
  lines from free ROM.
