# Scene syscalls (op 0F)

`syscall N`: A = `var.w[0]`, X = N * 2, `jsl C2:8B46` = `jsr ($8B4C,x)` with M16 X16, DB = $7E. Arguments are
`var.w[0]`, `var.w[2]`, `var.w[4]`, ... (`$7E:FEC3 + i`); answers go to `$0278` unless noted. 94 services, 79
used by the scenes. Names here are the listing's (`tools.scene_script.SYSCALLS`).

Read from the code (four readers, one range each), then checked by experiment (five more, one area each; the
tests are `tests/test_scene_{actors,entries,screen,sound,state}.py`). **H** code read fully, **M** mechanism clear
but not all of its meaning, **L** guess; **✓** reproduced in game by a test. 11 also sets bit 6 of the item's count
byte (cleared by 19), meaning unknown.

Test scripts: `assign(var(i), n)` is a byte store; arguments above 255 need `var(i, 1)`.

## Actors, effects

Actor n = record `$7E:2000 + n * 0x40`. Byte `+0x07` is a scripted mode: non-zero makes the actor update (C6:2DC0)
run C2:A8B2 (table C2:A8E9, modes 1-10, frame counter `+0x22`); a mode ends by clearing `+0x07` or by turning the
actor off (`+0x00` bit 7).

| N | name | what | |
|---|---|---|---|
| 1 / 3 | actor_vanish / _b | mode 1 / 3: squeezes into a thin tall line, then off (`+0x2C` width in 16ths, `+0x2D` vertical step, 0x100 normal); 1 raises the OBJ priority to 3 meanwhile | H ✓ |
| 2 / 4 | actor_appear / _b | modes 2 / 4: the reverse, grows back in 16 frames, after `actor_create`; 2 raises the priority | H ✓ |
| 21 | actor_jump | 32-frame hop, `[4]` x 9 px high, `[2]` signed x speed (not by facing), `[6]` pause between hops, repeated forever (0 = one hop); `[6] = 0xFFFF` vanishes at the end of the arc | H ✓ |
| 22 | actor_in_box | `$0278` = actor's tile in x `[2]..[6]`, y `[4]..[8]` (tile y = (`+0x16` + `+0x0A` - 16) / 8) | H |
| 23 | actor_squeeze_out | mode 7: narrows sideways only, then off ("Ils sont partis"); no fade, no mosaic | H ✓ |
| 24 | actor_sink_out | mode 8: flattens into the ground in 16 frames, then off; the read x jitter (C2:ACEC) does not show on `+0x13` | H ✓ |
| 28 | actor_set_move_bounds | `[2..8]` tile box x1, y1, x2, y2: `+0x03` bit 6, box at `$7E:E08B + n * 4` (checked C6:30C0) | H |
| 10 | give_actor_item | treasure actor (byte var[0x17]): item `+0x33`, flag `+0x35`, then `+0x02` bit 3. No site | M |
| 53 | actor_spawn_icon_copy | byte var[0x17] = actor: popup object over it (C6:D826). No site | M |
| 54 | leader_spawn_get_icon | A = icon kind: popup over the leader (C6:D826, template 0x2F, sound 0x12) | H |
| 50 / 51 / 52 | spawn_attr_0 / _2 / _3 | OBJ priority 0 / 2 / 3 (`$0460`) for attached actors (motion 15, spawner C6:4EA8) | H ✓ |
| 12 | effect_preset | A = preset 0-8 (C2:A81D): effect command list (C2:A42B), objects at `$7E:B073-B872`; `$095D = 3`. 1 fireball on the hero, 2 explosion at the screen bottom, 8 spark at a fixed spot; 0, 3-7 show nothing on map 123 | M |
| 13 | obj_frame_load | A sheet (C4:0000), `[2]` anim, `[4]` frame, `[6]` OBJ slot 0-8 (VRAM C2:A155): S-DD1 DMA of a 16x32 frame (VRAM diff) | H ✓ |
| 14 | obj_frame_load_wide | as 13, a 32x32 frame that also fills the next slot. No site | H ✓ |
| 15 | obj_sheet_load | A sheet: slots 0-8 = 3 anims x 3 frames (walk cycle per facing) | M |
| 16 | special | A = sub: 0/1 (one routine) 10 particles spawned below the screen, moved by fx 4 (C2:A2E4), 2 timer `[2]` frames with callback (C2:0AB9 / C2:0AF3), 3 full-screen sequence CC:0570, 4 full-screen setup C0:65D4 (ending) | 2: H, 0/1 M, else L |
| 17 / 18 | fx_channel_a / _b | A = handler 0-13 of C2:8ED7, `[2]` `[4]` its parameters: run each field frame (C2:00B8); B is the same code with `$056D` = 1. Handlers below | H |

### fx handlers (syscalls 17 / 18, table C2:8ED7)

| A | what | |
|---|---|---|
| 0 | stops the channel | H |
| 1 | command stream at `$0AF9`, only set up by the CC:0570 full-screen sequence: waits, bank FD pointers, ramps a grey triple; nothing on the field | M |
| 2 | 23 HDMA window / colour math scripts: 0-4 tinted disc shrinking on the hero (3 green), 5-11 white disc growing from him, 12 iris closing, 13 white haze, 14 sprites hidden in a band, 15 white dome, 16 / 18 / 19 black hole opening / opening and staying / closing, 17 black wobbling octagon, 20-21 faint orbs; most end alone (49-250 frames), 15 / 18 / 20 do not | H ✓ |
| 3 | 16 looping ambient sound scripts (e.g. 6: effect 500 three times every 70 frames), volume by the sound source (syscall 47 / op 1D) | H ✓ |
| 4 | moves syscall 16's 10 particles up and right | M |
| 5 | a fixed palette program, parameters ignored: black, then colours over ~250 frames (seen off its map only) | M |
| 6 | watches actors `[2]..[4]`: one touching the hero calls entry 2 / 0x7D (`$E90D`), 60-frame cooldown (scene 17's guards) | H ✓ |
| 7 / 8 / 9 / 10 / 13 | 16-colour cross-fade palette `[2]` → `[4]`: 7 colours 0xC0-CF (hero), 8 0xF0-FF every 32 frames, 9 the same every 8, 10 0xA0-AF, 13 BG palette 1 | H ✓ |
| 11 | lightning: random strikes, thunder (effect 11 / 12) at a random pan, one white frame from `$7F:2220`, palette back from `$7F:2020`; mode 2 restores and stops. Needs syscall 65's set-up first, a wait between (both use `$0589`) | H ✓ |
| 12 | raises one channel on the whole palette (1 blue, 2 red, 3 green), back over 32 frames, ends | H ✓ |

Game bug: 7-10 and 13 run their per-frame code with DB = $7F, so the step counter and the stop write land in
`$7F:0591` / `$7F:0571` and the channel never ends alone; scenes stop it with handler 0.

## Screen, palettes, VRAM

| N | name | what | |
|---|---|---|---|
| 5 | palette_fade_build | A steps, `[2]` from / `[4]` to palette id (C6:2378), `[6]` `$7F` buffer: blend steps of 0x70 colours (C2:9DBA) | H |
| 6 | palette_fade_build_alt | same into a second set `$04BC-04C0`, read back by C2:9D07 when the field returns from the menu (C2:6E8D, CB:022F), which rebuilds both sets | H ✓ |
| 7 | palette_fade_play | A frames per step, `[2]` delay, `[4]` steps, `[6]` buffer: NMI DMAs 0xE0 bytes to CGRAM colour 0x10 per step | H |
| 8 / 9 | screen_shake / _stop | A = amplitude: `$0254/$0256` (vertical, negated each frame by C2:0151); 9 clears | H |
| 25 | screen_set_main_sub | A = TM, `[2]` = TS: `$028E/F`, kept over map loads in `$0298/9` (`$FF` = map default) | H ✓ |
| 26 | screen_set_window_main_sub | A = TMW, `[2]` = TSW: `$0290/1`, override `$029A/B` | H |
| 27 | text_window_force_pos | A x, `[2]` y px: dialog window position (`$0492/3`); A = `$FFFF` back to automatic | H |
| 32 | vram_load_sdd1 | A = entry of C2:910C (27: VRAM address, S-DD1 source, size): NMI job 4, the VM pauses until done | H |
| 33 / 34 | vram_restore / vram_save | VRAM from / to bank $7F (table C2:922D) | H |
| 35 | cgram_load_7f | colours from bank $7F | H |
| 36 | cgram_load_palette | A 16-colour palette of C6:2585 | H |
| 37 / 38 | bg_freeze / bg_unfreeze | BG1-3 scroll freeze mask `$0437` | H |
| 39 | bg_set_scroll | BG scroll (`$0200` / `$0300` / `$0400` + 0x25 / 0x27) | H |
| 40 | color_math_set | CGWSEL / CGADSUB shadows `$0292/3` | H |
| 41 | palette_derive | A source palette, `[2]` RAM palette (0 = `$7F:2000`), `[4]` mode: 0 black, 255 white, 200 channels doubled (saturating), else halved; buffer only, rebuilt on menu return | H ✓ |
| 42 | letterbox_set | black bands of max(0, 4A - 32) lines top and bottom (measured A = 2-28); A = 0 turns the HDMA off | H ✓ |
| 58 | scroll_wave | A layers (1 BG1 H, 2 BG1 V, 4 BG2 H, 16 BG3), `[2]` amplitude px, `[4]` phase step (period 144 * 256 / `[4]` lines); the table is built only at a map load (C2:9F58 from C6:1157) | H (look L) |
| 63 | set_mosaic | A low byte → MOSAIC shadow `$0294` | H ✓ |
| 65 | palette_buffer_op | A = 0 zero fill, 1 white fill, 2 CGRAM DMA (NMI job) | H |
| 68 | sdd1_dma_to_wram | A = entry of C6:21A2. No site | H |
| 86 | display_reset | force blank, clear OAM / CGRAM, base palettes (C2:7FF8); after the ending | M |

## Party, items, money

Character records: 8 x 0x100 at `$7E:6FE1`, battle party = slots 0-3 at `$73E1-$76E1` (0 = leader). `+0x01` id
(counted from 1; scripts pass id - 1) in bits 0-5, bits 6-7 "away"; `+0x22` status (bit 0 KO, bit 3 poison);
`+0x50/52` max / HP; `+0x56/58` max / MP; `+0x9C/9E` equipment; `+0xD8` SP. Inventory: 512 slots, ids
`$7E:7FE1 + i`, counts `$7E:81E1 + i` (bits 0-5, bit 7 = id bit 8), max 20. Fol: 24-bit at `$0273`.

| N | name | what | |
|---|---|---|---|
| 11 | give_item | A item, `[2]` chest flag (flag2, set on success): answer in var.w[0] (0 ok, 1 full) and `$05B5` | H ✓ |
| 19 | take_item | A item, `[2]` count | H ✓ |
| 20 | add_fol | A added to Fol, capped at 9 999 999 | H ✓ |
| 29 | hero_force_run | the hero runs | H |
| 30 / 31 | party_heal_living / _all | heal the party; 30 skips status bit 2 | H |
| 43 / 44 | party_set_guest / party_clear_guest | record `+0x01` bit 6: guest, the menu shows "PNJ" for the level, out of battle; 44 a member again | H ✓ |
| 57 | party_bond_inc | relationship matrix `$0C38`, each active pair +1, capped at 10 | H |
| 59 | party_remove_member | A = character | H |
| 60 | roster_count | characters in all 8 records → `$0278`. No site | H |
| 61 | party_count_active | battle party size → `$0278` | H |
| 62 | party_get_ids | battle party ids → var.w[0..6] | H |
| 64 | party_damage_all | A = damage, bit 15 lethal | H |
| 70 | inventory_drop_type12 | removes items of categories 1 / 2 (C6:D88B); 70 and 77 split the inventory exactly, category 1 / 2 items are not in the Bagage list (what they are: M) | H ✓ |
| 73 / 74 | party_restore_hp / _mp | battle party HP / MP to max (73 also clears status) | H (73 ✓) |
| 75 | party_add_sp | A added to SP, cap 999 | H |
| 76 / 78 | inventory_stash / _unstash | inventory to / from `$7F:F800`, `$05B8` flag | H |
| 77 | inventory_keep_key_items | removes items of categories other than 1 / 2 (C6:D8C8) | H ✓ |
| 79 / 80 | party_solo / party_restore_solo | A alone as leader, others' ids kept at `$03F7`; 80 brings them back | H |
| 81 / 82 | char_restore_hp / _mp | one character | H |
| 84 | party_oracle_level | the party's best Oracle level → `$0278`: specialty 0x0A = rounded mean of savoirs 0x0E, 0x05, 0x0C (0 if one is 0); scene 89's "Antichambre de l'oracle Nv 2/4/6" doors | H ✓ |
| 89 | count_ladies_first | members with id in {2, 5, 9, 11, 12} (+ id 1 not leader) → var.w[0], var.w[4] ("Les femmes d'abord", scene 91) | H (code) |
| 90 | party_hp_to_1 | battle party HP to 1 | H ✓ |
| 91 | char_learn | A character, `[2]` spell / skill (`$7E:83E1 + slot * 0x20`) | H |
| 92 | remove_items_1ee_1f1 | items 0x1EE-0x1F1 out of equipment and inventory | H |

## Flags, state, sound

| N | name | what | |
|---|---|---|---|
| 0 | nop | `rts` | H |
| 45 / 46 | sin / cos | A in 2.5° steps (144 a turn) → `$0278`, 256 = 1.0 | H ✓ |
| 47 | sound_source_set_tile | point at tile x, y (x 8): read only by fx 3's C2:F877, volume (0x200 - min(0x200, 2 (\|dx\| + \|dy\|) / 3)) / 2 as command 0x2E p2, once at start (silent from 768 px; 0 on the source). No site | H |
| 48 / 49 | walk_slow_on / _off | `$F5` bit 0x40 | M |
| 55 | item_find_roll | with map flag `$0473 & 0x10`, 25% to queue kind 4 in `$05A4-05A6`: a script built at `$7E:6100` shows a sparkle and a message and adds an item | H ✓ |
| 56 | set_param_block | var.w[0..10] → `$0501-050B` (read by C2:EA1B, unread). No site | L |
| 66 / 67 | map_flags_set / _clear | `$0439` (from the map record): bit 0x10 palette animation on / off ✓; others BG scroll setup (M). No site | H / M |
| 69 / 93 | flag2_on / flag2_clear | flag A in `$7E:FE93` (op 5B's flags; C6:E402 / C6:E422) | H |
| 71 | battle_no_game_over | `$02C2` bit 0x20, survives battle_start; a party wipe was not forced, so the effect is not seen | M |
| 72 | keep_music_through_battle | `$02C2` bit 7: the next battle keeps the field music (no fade, no battle song, `$0972` = 1, cleared after); a map change still loads its music | H ✓ |
| 83 | set_var15 | var[0x15] = A unless already 2; 2 skips the random-encounter roll (C2:7029): no fight in 150 cave steps | H ✓ |
| 85 | sound_signal | releases the sound-sequence player's wait (`$98 = 2`): sound 519 loops until it, then fades, `$98` → 0 | H ✓ |
| 87 / 88 | mark_game_cleared / get_game_cleared | SRAM `$70:7E68 + [$70:7E67]` and `$05B1`; 88 → `$0278` | H (88 ✓) |

## Shared code and WRAM found on the way

- NMI jobs `$0581` / `$0589` through C2:1063: 4 S-DD1 → VRAM (C2:10E6), 5 RAM → VRAM, 6 VRAM → RAM, 7 CGRAM
  (C2:117B), 9 CGRAM DMA. Jobs 4-6 clear `$0231` bit 7, the "VM waits for the upload" flag.
- PPU shadows: `$028D` INIDISP, `$028E/F` TM/TS, `$0290/1` TMW/TSW, `$0292/3` CGWSEL/CGADSUB, `$0294` MOSAIC,
  `$C7` HDMAEN; script overrides `$0298-029B` (`$FF` = map default). BG structs `$0200` / `$0300` / `$0400`.
- Party: CC:0000 find record by id (carry clear = found, X = record), C8:0875 move a record to leader, C8:139F
  create a record, CA:C9B2 recompute party values, CA:D3BB slot → record, C2:724C all KO?, C6:E035 poison tick.
- Items: C6:D6B9 add, C6:D766 remove, C6:D798 find, C8:299F item record ((id - 1) * 0x25).
- Actors: C8:0768 free actor slot, C6:E2B9 actor from template (C6:5DEB), C6:D826 popup object, C3:8CB3 free an
  actor's sprite object.
- Effects: C2:9DBA palette blend, C2:A089 / C2:A2A4 OBJ frame load (S-DD1 DMA), C2:A42B effect commands,
  C0:4EB0 effect object alloc.
- Misc: CB:0923 random, CB:068F signed multiply, CB:0AC1 sine table, C2:0B51 wait for vblank, CC:043E sound
  effect panned by the leader, C0:8594 APU command, C0:1E64 sound-sequence player.
