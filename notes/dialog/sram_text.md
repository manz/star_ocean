# Scene text in SRAM (patch: src/dialog/sram_text.s)

Why: the scene text block unpacks whole into `$7E:B873`; the next WRAM user writes `$7E:D673` (7.5 KB). Japanese
peaks at 6.4 KB, the imported French at 13.1 KB (scene 60), 1 byte per letter already (codes < `$80`).

- Header `$FFD8` 3 -> 5: SRAM 32 KB. The board maps `$70-73:0000-FFFF` sized by the header. The game kept its
  saves at `$70:6000-7E6A` (three 0xA00 slots, then system bytes from `$7E00`), file offset 0 on 8 KB;
  src/core/saves.s moves its 120 operands down by 0x6000 to `$70:0000-1E6A`, so an 8 KB `.srm` loads as it is.
  The text pool is `$70:2000-7FFF` (24 KB); unpack and select rebase their offsets on `sram_text`. Boot writes
  `$70:08C3` once (`C0:CA72`, `sta $08C3` with DB = `$70`): slot 1 + 0x8C3, as on the 8 KB cart. Real-cart
  wiring for 32 KB unchecked.
- `scene_load_script` `C6:1137`: `jsl unpack` -> `text_unpack_sram` (container port: 0x81 / 0x83 / raw) into
  `sram_text` (`$70:2000`, 20 KB), size in `sram_text_size` after it. Same loop shape as the game's (flags `ror`ed out with a marker bit, one end check
  per item, DB = `$70` so literals are `sta.w 0,x`): 1.009x the game's cycles over all scenes.
- The two message selects, `C2:1C47` and `C2:1CAC` (`lda $B873,x / clc / adc #$B873 / sta $03D5`) ->
  `text_select_message`: copies message X/2 (offset to next offset, the last to the block size) to `$7E:B873`,
  cursor = `$B873`. Every reader (`lda.w 0,x`, DB `$7E`: C2:39E8, C2:423E, C2:3C0A, C2:3C31, C2:4093, ...) and the
  `FFFE` rewind (`$03D7`, set from X inside the message) stay untouched.

Checked: `tools/check_sram_text.py` (kintsuki: one `step()` after `run_frames` before setting registers, or the
core may be mid-instruction and the stub starts at a garbage address) (test_sram_text) runs both routines on all 94 scenes / 4012 messages against
the ROM; intro playthrough fetches the same 385 codes as the original.

Unpack: `C0:4C53`, dest = DB:X; non-`$7E` banks do literals with `sta.w 0,x` but back-references with a fixed
`mvn $7F,$7F`, so it cannot target `$70` as is.
