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

The entry slices are `$E613` (kind 0), `$E713` (kind 1), `$E813` (kind 2); the trigger lists follow in the same
cleared block (`scene_opcodes.md`, Triggers).

| entry | fired by |
|---|---|
| kind 2, id 0x7F (`$E911`) | A pressed in the field: C8:0000 (from C2:031B) pushes the pc and calls it, if the op at the pc is not FF |
| kind 2, other ids | the hero stepping on a `trigger_tile` / `trigger_zone` (ops 21 / 22; scanners C6:53BD, C6:54BB), as a call |
| kind 1 | an actor stepping on an `actor_trigger_tile` / `_rect` (ops 0B / 0C; C6:535B, C6:5446): run to the end (C2:1288) with the actor in `$0278` |

Kind 0 is not traced yet. The A script tests what it needs itself: scene 80's checks the hero's facing first
(`actor_get 0, 24` = `+0x18`, 0 up), then syscall 22 (C2:8F74): is actor `var.w[0]` (record `$7E:2000 + n * 0x40`)
inside tiles x `var.w[2]..var.w[6]`, y `var.w[4]..var.w[8]`, tile x = `$2013 / 8`, tile y =
`($2016 + $200A - 16) / 8`; `sys.w[7]` is `$0278`, its answer.

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
