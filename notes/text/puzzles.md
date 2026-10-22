# Word puzzles

Puzzles whose answer is spelled in the dialog: the French words change the answer, so the scene's event data
(the VM script behind the scene table's first pointer, unpacked to `$7E:3100`) may need edits too.
`tools/scene_events.py` holds them: same-length byte edits, checked against the ROM, packed and repointed.

## Scene 80: the door console (GAÏA)

- JP: the king's four phrases (39/68, 39/70, 80/6) start う ゆ き ち; the answer ちきゆう = チキュウ (Earth).
  FR: Acceptez / Indomptable / À vos héritiers / Gardez → GAÏA read backwards, the same order.
- Console: 80/10 picks one of four letter sets (set 4 is right), then 80/19-22 pick a slot per letter; a slot
  can't be reused, the 4th letter takes the slot left. Letters: message `28 + 4 * slot + (set - 1)`.
- Door test at event offset `0x396`: `07 <then> <else> 00 80 4c 00 04 01 00 80 4d 00 03 01 00 80 4e 00 01 01
  00 80 4f 00 02 ff` = set (var 4C) == 4 and slots (4D, 4E, 4F) == 3, 1, 2. VM expressions: `00` ==, `03` !=,
  `01` and between terms, `80 nn` byte var, `81 nn` word var, `00 nn` / `01 lo hi` constants (as read here).
- FR set 4 is `A I G A`: G slot 3, A slot 1 or 4, I slot 2. Letter 2's test becomes a second `set == 4`, so
  either A passes.
- The edited events are written over the original block at `$E6:D54D` (it packs 3 bytes smaller). A first build
  moved them to ROM pages 6-7, which the game's `unpack` cannot read: the scene loaded open bus.
- The console is the room's A-button script (entry 2/0x7F, L00be): map 164, `var.w[0x10] == 144`, hero inside the
  `op_0f` box. Not yet played to the door in the emulator.
