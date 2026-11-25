# Fight popups

- Shared OBJ sheet `D9:0000`: S-DD1, 8 KB of 4bpp tiles, 4038 B compressed, the next stream right behind it.
  `C0:23C3` DMAs it to VRAM word `$7000` (OBJ tiles `$100-$1FF`, OBSEL 3) on every map load; fights draw from it.
  Only reader: source operands at `C0:23D3` (address) and `C0:23D9` (bank).
- Tile row 14 (OBJ `$1E0-$1EF`): Short `0-2`, Long `3-4` (the L / R special's range), Guard `5-7`, Guts!! `8-10`,
  Heal `11-12`, MISS!! `13-15`. Letters are ink on rows 1-6, top three rows one colour, bottom three another, with a
  colour 1 outline. Row 13: the big digits; row 15: small digits.
- Patch (`src/battle/popups.s`, `tools/battle_obj.py`): Court / Long / Garde / Cran!! / Soin / Raté!!. The redrawn
  sheet packs to 4043 B, so the stream moves to the text16 pool and the two operands point there.
- Not done: the command ring labels (SPECIAL, CHANGE, TACTICS, RUN, ITEM, SKILL): S-DD1 cels streamed to
  `$7F:E000` each frame and DMA'd to VRAM word `$6000` by `C1:01BA`.
