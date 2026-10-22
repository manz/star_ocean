# Battle timing (vanilla slowdown)

Measure with `uv run python -m tools.battle_bench [--profile]` (states `tests/states/battle_chest.kss`,
`battle_busy.kss`). Same numbers on the unpatched ROM: chest 17 late, busy 34 late / 10 lost.

- Battle loop: one iteration per 2 frames (30 fps). Update `C3:8D3D` is called at `C1:0147`; the loop
  waits for the NMI flag `$D9` in `C0:84AB` (from `C1:019B`) and for vblank in `C0:8496` (from `C1:0316`).
- Slowdown is the original game's: when an iteration misses its vblank the gap is 3 or 4 frames. When
  the next one catches up (gap 1), you see a stutter; when it doesn't, the battle slows down.
  - Early fight, chest animation (`battle_chest`, mash A): 3, 1, 2, 2 every 8 frames,
    with the logic tick and a burst of about 30 cel streams on the same frame.
  - Late party with spells (`battle_busy`): 37 late iterations out of 322, only
    16 caught up; 274 of 600 frames have under 15% idle.
- No single hotspot on the overrun frames: `C3:917C` (sprite cels) is about 11%, then many small
  routines at 2-5% each. The game runs at its CPU limit during busy fights.
- `C3:917C` streams each cel by S-DD1 DMA into WRAM through `$2180`: 0x20 B (8x8) or two 0x40 B DMAs
  (16x16), each started after waiting for H-blank (`bit $4212` / `beq`). HDMA is on in battle (ch5
  `$2111`, ch6 `$2132`, ch7 `$2130`, tables in `$7E`), so the wait keeps HDMA from cutting a stream in half.
  - Only 5-9% of streams repeat the previous frame's (source, size, destination): caching won't help.
  - With the waits patched out (soft IPS, kintsuki): 342 iterations instead of 322 in the late fight,
    the same 35 late ones; nothing changes in the early fight. Not worth the risk on hardware.

## Why a pass is late

- Pacing: `C1:019B` waits for the IRQ flag `$D9` (V-IRQs at lines 216 and 258, `$4209`), then `C1:0310` waits
  one more vblank unless `$E1` (vblanks since the last pass) is already 2. A pass whose work runs past the
  IRQ waits nearly a whole frame: late passes are mostly idle, not over by a hair (patching the H-blank waits
  out saves ~6% of a frame and leaves every late pass late).
- The logic block (`C1:00D0`: `C1:36E9`, `C9:0000` actors, `C3:14B2`, `C1:80E5`, `CC:431A`, `C0:5121`, ...)
  runs every pass in a fight. Once `$0974` is set (battle won) and `$0975` is 0, it runs only when
  `$E4 & 3 == 0`, one pass in 4: the victory slow motion. That one pass carries about 6700 instructions
  before the update (about 780 otherwise) and misses the IRQ: the chest-phase hitch every 8 frames.
  - `C9:0000`: actor slots `$7E:E100 + n * $100`, a handler each through a jump table (3375 instructions
    in that pass); `C0:5121` scans 64 slots of $20 at `$7E:B073`, `C1:80E5` 64 slots of $40 at `$7E:C073`
    (about 27 cycles per empty slot).
- Audio: the IRQ (`C0:02C8` > `C0:032D` > `C0:05E5`) streams to the SPC700 in 3-byte handshakes
  (`C0:050F` / `C0:073E` pick one of 8 unrolled senders, `C0:09F0` sends 75 bytes); the SPC loop at `$2170`
  takes about 46 SPC cycles a packet, so a 75-byte send costs about 8% of a frame. Not the trigger: most
  late passes have no send.
- `C1:0360` polls `$4212` bit 0: the joypad auto-read, about 3 lines after vblank.
