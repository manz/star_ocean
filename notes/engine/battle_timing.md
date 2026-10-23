# Battle timing (vanilla slowdown)

Measure with `uv run python -m tools.battle_bench [--profile]` (states `tests/states/battle_chest.kss`,
`battle_busy.kss`): it counts the frames where the sprites move (OAM's position table changes). Same numbers on
the unpatched ROM.

## Pacing

- Battle loop: one pass per 2 frames (30 fps). Update `C3:8D3D` is called at `C1:0147`; the pass then waits for
  the IRQ flag `$D9` in `C0:84AB` (from `C1:019B`; V-IRQs at lines 216 and 258, `$4209`), does its forced-blank
  DMA, and `C1:0310` waits one more vblank in `C0:8496` unless `$E1` (vblanks since the last pass) is 2.
- Where the update is called moves around inside a pass (the logic block runs first); that is not what the
  screen shows. Time passes by the sprites (OAM) or by kintsuki's `live_counters()` (master clock, scanline,
  dot), exact inside callbacks: the battle IRQs land on lines 216 and 258. `master_cycles` / `cpu_cycles` jumped
  across scheduler reduces before kintsuki 93e442b (not released yet).

## Victory slow motion (by design)

- The logic block (`C1:00D0`: `C1:36E9`, `C9:0000` party actors, `C3:14B2`, `C1:80E5`, `CC:431A`, `C0:5121`,
  ...) runs every pass in a fight. Once `$0974` is set (battle won) and `$0975` has counted down, it runs only
  when `$E4 & 3 == 0`: one pass in 4, the sprites step every 8 frames (7.5 fps). That is the "lag" around the
  chest; the steps are regular (`battle_chest`, frames ~200-290).
- Tried (reverted): spreading that block over 3 passes. Nothing to fix: the steps were already regular.

## Busy fights (real slowdown)

- `battle_busy`: 38 late steps (3-4 frames) in 600 frames, 32 caught up. Same on the unpatched ROM.
- Sprite pipeline, every pass: 5.6-8k instructions outside the waits, most in `C3:8D00-92FF`: the OAM builder
  loop `C3:8F5E-9083` (about 55 instructions a sprite piece, about 41 pieces) and the cel streamer `C3:917C`.
- `C3:917C` streams each cel by S-DD1 DMA into WRAM through `$2180`: 0x20 B (8x8) or two 0x40 B DMAs (16x16),
  each started after waiting for H-blank (`bit $4212` / `beq`). HDMA is on in battle (ch5 `$2111`, ch6 `$2132`,
  ch7 `$2130`, tables in `$7E`), so the wait keeps HDMA from cutting a stream in half. Only 5-9% of streams
  repeat the previous frame's (source, size, destination): caching won't help. Without the waits
  (`CEL_DMA_ANYTIME`, `src/engine/cel_dma.s`; CPU rev 1 DMA/HDMA crash risk) busy 37 -> 29 late,
  chest 15 -> 11.
- `C9:0000`: party actor slots `$7E:73E1 + n * $100` (4), a handler each through `jsr (C9:003D,x)`.
  `C0:5121` scans 64 slots of $20 at `$7E:B073`, `C1:80E5` 64 slots of $40 at `$7E:C073` (about 27 cycles per
  empty slot).
- Audio: the IRQ (`C0:02C8` > `C0:032D` > `C0:05E5`) streams to the SPC700 in 3-byte handshakes (`C0:050F` /
  `C0:073E` pick one of 8 unrolled senders, `C0:09F0` sends 75 bytes); the SPC loop at `$2170` takes about
  46 SPC cycles a packet, so a 75-byte send costs about 8% of a frame.
- `C1:0360` polls `$4212` bit 0: the joypad auto-read, about 3 lines after vblank.
- `C5:035D`: animation frame lookup ((duration, word) entries from `[$BE]`, `$20` = time; 0 ends, `$FF` loops), about
  9 calls and 30 entries a frame; Y-indexed in `src/engine/battle_speed.s` (busy 29 -> 28 late).
- `C3:8F5E`: OAM piece loop; objects without rotation (`$FA`, `$FC`) or vertical flip (`$21` bit 7) take a loop without
  the per-piece tests (`src/engine/battle_speed.s`). Update `C3:8D3D` from 24 battle snapshots: 37.0% -> 36.2% of a
  frame; too small for the bench to see (busy 28 -> 29, noise).
- Battle IRQs: line 216 forces blank and runs the DMA list (`C0:0010`, palette from `$7E`), sets `$D9`; line 258 turns
  the screen on, clears `$D9` and calls the audio service `C0:032D` (sample stream through S-DD1 banks E0-FF,
  `$4806/7` remapped, 0x4E-byte blocks from `$51-$53`). `C0:84AB` waits for `$D9` clear then set.
- `AUDIO_DEFERRED` (`src/engine/audio_defer.s`, off): the line-258 IRQ marks the send, `C0:84AB` sends it if the line
  is under 160 (latched `$2137` / `$213D`, `$4201` bit 7 set), else the next IRQ does. Streams stay contiguous.
  busy 29 -> 26, chest 11 -> 13; without audio at all (ceiling) 23 / 7. Sending past line ~190 eats the DMA window.
- Names (`C0:3FA3` draws one into the window tilemaps `$7E:5100` / `5900`): five copies of a reader (`C0:3FBC`, `40BF`,
  `41F1`, `49CF`, `CA:BE03`) scan the 893 ids at `D7:06FA` one at a time, about 8 us each: 0.73 ms a name. Window
  redraws `C1:5619` (3 names) and `C1:59D5` (about 4) push passes to 3 frames. The ids are 20 runs of consecutive
  values; `NAME_INDEX` (`src/engine/name_index.s`) finds the run: `C0:3FA3` 0.73 -> 0.11 ms, `C1:5619` 5.0 -> 1.8 ms,
  `C1:59D5` 7.5 -> 5.8 ms. Timeline (A mashed, 300 frames): 3-frame passes 16 -> 12. Bench: busy 29 late either way,
  steps 222 -> 258, caught up 18 -> 31; chest unchanged. Left in `C1:59D5`: `C0:4501` and `C1:517D`.
