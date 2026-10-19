# String databases (non-dialog)

All four share one lookup shape (`C2:3FF4`, `CA:B24C`, `CA:B278`, `CA:B2B0`): linear scan of a 0-terminated
u16 id list, same index into a u16 offset list, offset + string base. `CA:B2B0` routes ids ≥ `EA60` to the
`$7F` copy of `menu16`, below to `battle16`.

| db | ids | offsets | base | enc | count | content |
|---|---|---|---|---|---|---|
| names8 | `D7:06FA` | `D7:0000` | `D7:0DF6` | 8×8 | 893 | party, items, skills, spells, enemies |
| labels8 | `FE:A5CE` | `FE:A2E0` | `FE:A8BE` | 8×8 | 375 | menu labels / prompts (ids `EA60+`) |
| battle16 | `D7:2A8D` | `D7:254B` | `D7:2FD1` | 16×16 | 673 | battle + system messages, short descriptions |
| menu16 | S-DD1 `FE:612F` → `$7F:2000` | S-DD1 `FE:5CF0` → `$7F:2800` | LZ `FE:63A1` → `$7F:3000` | 16×16 | 950 | menu help, item / skill descriptions |

Encodings:
- 8×8 (`CA:BCAD`, tilemap writer into the BG shadows `$7E:3100/3900/4100`): byte = tile in the menu font
  (`DB:A078` → VRAM `$2000`), `C0-E8` voiced (tile `CA:BE98[c−C0]` + ゛ tile B2 on the row above),
  `E9-F2` semi-voiced (`CA:BEC1[c−E9]` + ゜ B3), `FC` newline (+2 rows), `FF` end. `BF` is the padding blank.
- 16×16 (`C6:F6F9` by id, `C6:F7D0` by pointer): u16 code, glyph = code − 0x10 (dialog font, `C8:0C3C`
  blits 2bpp into `$7F:E000` → VRAM `$6000`), `000D` newline, `FFFF` end.

Several ids share one offset (unused slots point at the same string).
The `FE:A700` block before `labels8` is the name-entry character grid, not strings.
