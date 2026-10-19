# S-DD1

- Used for graphics, mostly decompressed into WRAM via `$2180` then copied.
- `C3:917C`: per-frame sprite cel streams (0x40 B) → `$7F:E000..`.
- `C2:FDF0`: title/name-screen anims. `CA:6328`: menu / name-entry gfx. `C2:E07E`: intro text bitmaps.
- kintsuki: `e.sdd1_streams(data=True)` logs every stream (head, ROM offset, compressed size, WRAM/VRAM
  target, caller); `e.sdd1_decompress(addr, size)` decodes any stream offline.
- `tools/sdd1.py`: pure-Python codec. `decompress_bytes` matches the chip byte for byte (data + compressed size,
  checked against ares on 6 game streams); `compress` tries the 16 headers, output is smaller than the game's
  (font `DB:A078`: 1954 → 1952; the French 8x8 font packs to 1905, so it fits in place).
