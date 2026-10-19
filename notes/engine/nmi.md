# NMI jobs

- Runner `C2:0B5E` (code around `C2:0D00`). Job bits in `$F3` / `$F4`, tested with `asl`.
- S-DD1 jobs: `$4800=1`, DMAP `$09` (fixed A-bus), source from `$04C4`/`$04D5`…, `$4801=1`, MDMAEN,
  then `$4800=0`.
- `C2:0EF5`: per-glyph DMA of the dialog framebuffer (`$7E:A353..` → VRAM `$5940..`).
