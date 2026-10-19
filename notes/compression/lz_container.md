# `C0:4C53` container

Call: `A` = source bank, `Y` = source address, `DB:X` = destination (bank 7E or 7F).

Header (9 B): `type`, `len16` @+1 (payload bytes), `rawlen16` @+5; payload @+9.

| type | codec |
|---|---|
| `0x81` | LZSS |
| `0x83` | LZSS + RLE |
| other | raw copy of `rawlen+1` bytes |

LZSS: flag bytes read LSB-first, bit 1 = literal byte, bit 0 = match `b0 b1`:
dist = `b0 | (b1 & 0x0F) << 8` (back from the output cursor), len = `(b1 >> 4) + 3`.

`0x83` extra, when `b1 >= 0xF0`: `n = b1 & 0x0F`
- `n != 0`: `b0` repeated `n + 3` times (2 B)
- `n == 0`: `src[p+2]` repeated `b0 + 0x13` times (3 B)

A Python decoder matched 10/10 live calls bit-exact (all three types).

Known calls (scene loader `C6:0911`): `FF:C800` → `$7F:0000` (0x8000), `E6:B87D` → `$7E:3100`
(scene data, `C6:10FF`), `E8:41FC` → `$7E:B873` (scene script, `C6:1137`).
