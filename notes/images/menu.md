# Menu graphics

Loaded by `CA:6328` with hard-coded immediates (no table).

| source | size | VRAM | content | translate |
|---|---|---|---|---|
| `FE:4B5B` (`CA:6533`) | 0x800 4bpp OBJ | `$7400` | element icons with baked kanji 地 水 火 雷 風 光 闇 無 + 2 status | yes |
| `FE:3CAD` | 0x1000 4bpp OBJ | `$6C00` | A/B/X/Y/L/R prompts, arrows | no |
| `FE:4771` (`CA:E4D9`) | 0x400 | - | item category icons (NEW, BTL, …) | no |
| `FE:452D` (`CA:0666`) | 0x800 | - | cursors, gauge | no |
| `FE:58E4` (`CA:0884`) | 0x600 | `$7F:1800` | button frames | no |

Title, copyright, VRSS / DUET logos, "New Game / Continue / Sound Player": already English.
Battle graphics: not surveyed yet.

## Choice bubbles (field yes / no)

Sprite frames (`C3:8ECB` format) in the `C4:221B..` frame list (emotes, numbered discs, bubbles), cels streamed
by `C3:917C` from bank `EE`. The selected answer shows the large bubble, the other the small one.

| frame | size | content |
|---|---|---|
| `C4:2409` | 48x24, 3 16x16 + 6 8x8 cels | はい, selected (2 px strokes, 2 px shade) |
| `C4:2457` | 48x24, 3 16x16 + 6 8x8 cels | いいえ, selected |
| `C4:22F2` | 32x16, 2 16x16 cels | はい, not selected (1 px strokes, 1 px shade) |
| `C4:2307` | 32x16, 2 16x16 cels | いいえ, not selected |

Patched by `tools/yes_no.py` → `src/dialog/yes_no.s` ("Oui" / "Non"). A 16x16 cel's bottom stream sits at
source + the record's last byte, not where the top stream's decode stops.
