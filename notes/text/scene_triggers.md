# Scene triggers and map changes

How a scene's event data starts, what runs its trigger scripts, and how to reach a map the way the game does.

## Header and scene load (C2:36E2)

- Header: u16 length, u16 start-up offset (0 in every scene seen: right after the header), then 4-byte entries
  (kind, id, u16 address relative to the header's end) up to an FF.
- Load clears `$7E:E613-EE72`, then each entry stores its absolute address at
  `$7E:E613 + kind * 0x100 + (id * 2 & 0xFF)` (the shift runs in 8 bits: ids from 0x80 alias the low ones).
- pc = header end + start-up offset, `$0234 = 1`, stack `$FE = $FFF2`, `$023B-0243` / `$055E-0560` cleared, then
  one VM pass (C2:1258).
- Start-up code: `call setup; loop: wait 1; goto loop`. The setup branches on the map id (`sys.w[0xc]`) and story
  state, places actors and sets up the map's triggers.

## What fires an entry

| entry | fired by | seen at |
|---|---|---|
| kind 2, id 0x7F (`$E911`) | A pressed in the field: C8:0000 (from C2:031B, in the VM's frame path) pushes the pc and calls it, if the op at the pc is not FF | scene 80 L00be |
| kind 1 (`$E713 + x`) | C6:54A8: run to the end (C2:1288) with the pc saved and restored | not mapped to an id yet |
| zone table `$EB8E + 5n` | C6:54BB while walking: hero tile against x1, y1, x2, y2 for each zone, `$0241` the table end | exits, probably kind 2 0x24-0x26 in scene 80 |

Which opcode fills the zone table, and kind 0, are not traced yet. The A handler tests the hero's position itself:
scene 80's script calls syscall 22 (C2:8F74): is actor `var.w[0]` (record `$7E:2000 + n * 0x40`) inside tiles x
`var.w[2]..var.w[6]`, y `var.w[4]..var.w[8]`, tile x = `$2013 / 8`, tile y = `($2016 + $200A - 16) / 8`. Then
`sys.w[7] == 1`: in game the console answers only with the hero facing up, so likely the result or the facing.

## Map change: op 24 (C2:2112)

`24 map, kind, x, y, facing`: `$0461` map, `$045A` kind, `$0463 = x * 8`, `$0465 = y * 8 - 16`, `$0467` facing.
Kind 0 requests the fade out (`$04A0 = 0x100`, `$049D |= 0x80`); kind 2 also works from the hero's position
(C2:2162). All kinds then stop the VM until the new map (`$0468`, `$0234`, `$024F`) and clear the field state
(C2:21F7). The new map loads its scene's event data and runs its start-up.

## Reaching a map in a test

Load a save into the field, write `24 map, 0, x, y, facing; loop: wait 1; goto loop` (`tools.scene_asm`) into the
scene's event buffer, point `$0238` at it with `$0234 = 1`, `$0231 = 0`. The game then fades out and arrives as on a
real door: name banner, actors and the scene's start-up. Story variables (`$7E:FEC3 + index`) can be set before.
Example: scene 80's console room is map 164 at (8, 8) facing 2 with `var.w[0x10] = 144`; `tests/warp.py` does it
and `tests/test_scene80.py` plays the console from there.

Writing a scene's event data to `$3100` and pointing the pc into it (the first attempt) skips the start-up: no
sprites, wrong camera.
