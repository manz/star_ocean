# Dialog script

- Scene table `E4:0000`: 94 × 6 B, indexed by scene id − 1 (`C6:10E0`):
  event-data LZ ptr (→ `$7E:3100`), text LZ ptr (→ `$7E:B873`). Scene id comes from `$7E:8764,x`;
  the text block is only reloaded when it differs from `$0233`.
- Text block: u16 offsets to messages (count = first offset / 2), then the streams. 4012 messages total.
- Stream (`C2:39DB`): code byte, bit 7 set → 2 bytes `(b0 & 7F) | b1 << 7`. `FFFF` end, `FFFE` rewind to `$03D7`.
- `5 ≤ code ≤ 0x4000` → glyph `code − 5` (`C2:63A0` blit; `$048B == 9` → `C2:68EE` variant).
- Controls, handler `C2:3B2F[(code + 1) & 0xFF]`:

| code | name | args | notes |
|---|---|---|---|
| 0000 | nl | 0 | x = 0, y += 0x10 + spacing |
| 0001 | page | 0 | wait + clear framebuffer |
| 0002 | str | 1 | insert string id (speaker / party names) via `C2:3EE3` into `$051A` |
| 0003 | speed | 1 | `$03ED` |
| 0004 | color | 1 | `$03DE`; ≥ 3 → palette from `C2:6A0D` |
| 4001 | var | 1 + varint | number / table value (`C2:3D3C`) |
| 4006 | item | 2 | `C2:3FF4` looks the id up in the D7 names DB |
| 4007/8 | mode | 1 | `$03D1` |
| 4009 | pos | 2 | x, y (`$03D9/$03DA`) |
| 400A | spacing | 2 | `$03DB/$03DC` |
| 400B | narration | 1 | screen id → pre-rendered lines (see `images/narration.md`) |
| 400C | leader | 0 | name of party member `$0278` |
| 400D/E | member | 0 | `C2:3FA3` |

Inserted strings run through `$051A` with the cursor parked in `$03D7`.
