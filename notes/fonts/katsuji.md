# Fonts (katsuji)

All text fonts are katsuji's bundled sumi family (`katsuji.toml`, `uv run katsuji build`, run by `tools.patch`):

- `sumi/16` (8x16): the dialog VWF on `text/so_fr.tbl` → `build/gen/dialog_font.dat`; the 16x16 menus
  (menu16, battle16) draw from the same glyphs (tools/menu_font16.py).
- `sumi/8`: the menu 8x8 VWF. tools/vwf8.py bakes labels8 / names8 / Talent names with it (uppercase accents sumi/8
  lacks folded to their letter, icons and codes it lacks kept as menu font tiles) and tools/pen8.py feeds the runtime
  pen (party names) the same glyphs, both straight from `katsuji.fonts.bundled("sumi/8")`: no katsuji.toml entry.
