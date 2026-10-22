# Star Ocean (J): RE notes

One folder per component, small files. Labels for every address live in `so.kintsuki/`
(load the base ROM `Star Ocean (Japan).sfc`).

- `rom/`: cart, board, bus mapping
- `engine/`: scheduler, NMI jobs, battle timing
- `compression/`: S-DD1, `C0:4C53` LZ container
- `dialog/`: script stream, glyph blit, font, framebuffer, scene text in SRAM, VWF + 8 MB pages (patch)
- `vram/`: per-screen VRAM layout, 8x8 VWF budget
- `fonts/`: game fonts, katsuji assets
- `text/`: dialog script, string databases, character tables
- `images/`: graphics with Japanese text (narration, menu sprites)

Patch: `uv run python -m tools.patch` (a816 → `build/star_ocean.ips` + soft-patched `build/star_ocean.sfc`).
Tools: `uv run python -m tools.dump_font`, `uv run python -m tools.dump_images`, `uv run python -m tools.dump_text` (fonts/images → gitignored `extracted/`; text → `text/script/`, `text/menu/`).
