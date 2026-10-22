# Battle timing (vanilla slowdown)

- Battle loop: one iteration per 2 frames (30 fps). Update `C3:8D3D` is called at `C1:0147`; the loop
  waits for the NMI flag `$D9` in `C0:84AB` (from `C1:019B`) and for vblank in `C0:8496` (from `C1:0316`).
- Slowdown is the original game's: when an iteration misses its vblank the gap is 3 or 4 frames. When
  the next one catches up (gap 1), you see a stutter; when it doesn't, the battle slows down.
  - Early fight, chest animation (`star_ocean_battle_mash_a.kss`, mash A): 3, 1, 2, 2 every 8 frames,
    with the logic tick and a burst of about 30 cel streams on the same frame.
  - Late party with spells (`star_ocean-battle-items.kss`): 37 late iterations out of 322, only
    16 caught up; 274 of 600 frames have under 15% idle.
- No single hotspot on the overrun frames: `C3:917C` (sprite cels) is about 11%, then many small
  routines at 2-5% each. The game runs at its CPU limit during busy fights.
- `C3:917C` streams each cel by S-DD1 DMA into WRAM through `$2180`: 0x20 B (8x8) or two 0x40 B DMAs
  (16x16), each started after waiting for H-blank (`bit $4212` / `beq`). HDMA is on in battle (ch5
  `$2111`, ch6 `$2132`, ch7 `$2130`, tables in `$7E`), so the wait keeps HDMA from cutting a stream in half.
  - Only 5-9% of streams repeat the previous frame's (source, size, destination): caching won't help.
  - With the waits patched out (soft IPS, kintsuki): 342 iterations instead of 322 in the late fight,
    the same 35 late ones; nothing changes in the early fight. Not worth the risk on hardware.
