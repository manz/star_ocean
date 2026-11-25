# Fight popups

- Shared OBJ sheet `D9:0000`: S-DD1, 8 KB of 4bpp tiles, 4038 B compressed, the next stream right behind it.
  `C0:23C3` DMAs it to VRAM word `$7000` (OBJ tiles `$100-$1FF`, OBSEL 3) on every map load; fights draw from it.
  Only reader: source operands at `C0:23D3` (address) and `C0:23D9` (bank).
- Tile row 14 (OBJ `$1E0-$1EF`): Short `0-2`, Long `3-4` (the L / R special's range), Guard `5-7`, Guts!! `8-10`,
  Heal `11-12`, MISS!! `13-15`. Letters are ink on rows 1-6, top three rows one colour, bottom three another, with a
  colour 1 outline. Row 13: the big digits; row 15: small digits.
- Patch (`src/battle/popups.s`, `tools/battle_obj.py`): Court / Long / Garde / Cran!! / Soin / Raté!!. The redrawn
  sheet packs to 4043 B, so the stream moves to the text16 pool and the two operands point there.
- Popup letters are kerned pairwise (`tools/obj_letters.py`): a letter moves left while a blank column stays between
  it and the previous one on its row and the rows next to it.
- "SKILL!": frame `C8:84C4` (OBJ `$1A6` `$1CA` `$1B6`, only user), a sibling of the Guts!! (`C8:79B8`) and MISS!!
  (`C8:79D9`) frames, all played from the script table `C8:76E0`; likely a combat skill going off (the manual: skills
  "trigger special effects ... at a given rate"). Rare: never seen in ~25k frames of mashed fights. Patch: Talent!,
  kerned to 24 px in place.

# Command ring labels

- `C1:4F36`: 5 entries (flags, dx, dy, 16-bit pointer) to the 32x32 icon frames; `C1:4F4F`: 5 entries (`0x20`,
  16-bit pointer) to the label frames. Frames are the `C3:8ECB` format; `C3:917C` streams each cel (S-DD1, `0x20` per
  8x8) into `$7F:E000+` and the NMI DMAs it to VRAM word `$6000`.
- Label frames, 8x8 cels, 6-row capitals in colour 15 with a colour 1 outline: SPECIAL `C1:5052` (4 cels), ITEM `5075`
  (3), RUN `5090` (2), TACTICS `50A3` (4), CHANGE `50C6` (4). Streams `DC:1113-DC:12A0`.
- Patch (`src/battle/ring_labels.s`, `tools/ring_labels.py`): SPECIAL / OBJET / FUIR / TACTIQUE / ECHANGE in the same
  cel counts (STRATEGIE, the menu's word, needs 35 px; capitals take no accent); the cel records point at new streams in text16.
