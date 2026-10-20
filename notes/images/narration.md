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

## French (src/dialog/narration.s)

- `text/fr/narration.toml` → `tools/narration.py`: Helvetica 12 drawn at 4×, box-filtered to the 3 greys; the
  letter's Japanese ink is erased (ink not touching the torn edge takes the paper around it), French drawn in ink.
- Streams go in the `text16` pool, which narration.s grows with the 19 freed Japanese slots and the 0xFF padding
  before the FE / FF bank ends. 13 French lines are ≥ 255 B against 12 freed slots that size: no in-place fit.
- Scene 30 is the Calnus intro (`[narration][1..c]`). Its other subtitles (爆発の際…, シールドしろ, 宇宙暦346年…)
  are a different path: sprite cels copied by `C3:944C` from a per-cutscene 16×16 4bpp glyph sheet in WRAM
  (e.g. `DB:98CB` → `$7F:21A0`, loaded by `CC:1715`). Credits (job titles, names) are `C2:DB33` streams
  (0x400 B → VRAM `$5000` title / `$5200` name). Both untranslated.

## Cutscene text (src/dialog/cutscenes.s)

- Sprite frames, parsed at `C3:8ECB`: an object's sprite list (bank CC, 5-byte entries `[flags][dx][dy][frame]`)
  points at frames `[count][w / 4 - 1][h / 4 - 1]` + cels `[size][dx s16][dy s16][src 24]`. A WRAM source
  (`$7F`) is a 0x80-byte cel copied by `C3:9336`; a ROM source is two 0x40-byte S-DD1 streams (top, bottom tile
  pairs), the second at src + one more byte (9-byte cel). The first cel's bank picks the kind for the whole frame.
- `text/fr/cutscenes.toml` → `tools/cutscene_text.py`: ENIX / tri-Ace openers, the intro subtitles, three job
  titles. Frames go in a bank CC pool of the freed Japanese frames + the padding from `CC:FC60`; cels in text16.
- BG3 credit titles: `C2:DB33` streams, 256x16 2bpp as two 128-px halves (16 tiles top row, 16 bottom). Credits
  script `C2:DA57`: op 02 = title, 03 = name (24-bit operands), 04 wait, 05 …
