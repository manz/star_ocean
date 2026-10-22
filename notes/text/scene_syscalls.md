# Scene syscalls (op 0F)

`syscall N`: A = `var.w[0]`, X = N * 2, `jsl C2:8B46` = `jsr ($8B4C,x)` with M16 X16, DB = $7E. Arguments are
`var.w[0]`, `var.w[2]`, `var.w[4]`, ... (`$7E:FEC3 + i`); answers go to `$0278` unless noted. 94 services, 79
used by the scenes. Names here are the listing's (`tools.scene_script.SYSCALLS`).

Read from the code (four readers, one range each), so each row has a confidence: **H** code read fully, **M**
mechanism clear but not all of its meaning, **L** guess. **✓** = checked in game (warp + injected script, see
`scene_triggers.md`): 20, 25, 45, 46, 63, 73, 88, 90 behaved as written; 11 / 19 too, and 11 also sets bit 6 of the
item's count byte (cleared by 19), meaning unknown.

## Actors, effects

Actor n = record `$7E:2000 + n * 0x40`. Byte `+0x07` is a scripted mode: non-zero makes the actor update (C6:2DC0)
run C2:A8B2 (table C2:A8E9, modes 1-10, frame counter `+0x22`); a mode ends by clearing `+0x07` or by turning the
actor off (`+0x00` bit 7).

| N | name | what | |
|---|---|---|---|
| 1 / 3 | actor_vanish / _b | mode 1 / 3: `+0x2C` 0x10 → 1, `+0x2D` ramps down over 16 frames, then off (1 also sets `+0x0F` bits 0-1) | M |
| 2 / 4 | actor_appear / _b | modes 2 / 4: the reverse, after the actor is created (`op_2b`) | M |
| 21 | actor_jump | `[2]` x speed (8.8), `[4]` height factor, `[6]` glide frames: mode 5 parabola; `[6] = 0xFFFF` mode 6, hop away and vanish | M |
| 22 | actor_in_box | `$0278` = actor's tile in x `[2]..[6]`, y `[4]..[8]` (tile y = (`+0x16` + `+0x0A` - 16) / 8) | H |
| 23 | actor_fade_out | mode 7: `+0x2C` 0x10 → 1, then off ("Ils sont partis") | M |
| 24 | actor_vanish_shake | mode 8: x jitter (C2:ACEC) ~0x38 frames, then off | H |
| 28 | actor_set_move_bounds | `[2..8]` tile box x1, y1, x2, y2: `+0x03` bit 6, box at `$7E:E08B + n * 4` (checked C6:30C0) | H |
| 10 | give_actor_item | treasure actor (byte var[0x17]): item `+0x33`, flag `+0x35`, then `+0x02` bit 3. No site | M |
| 53 | actor_spawn_icon_copy | byte var[0x17] = actor: popup object over it (C6:D826). No site | M |
| 54 | leader_spawn_get_icon | A = icon kind: popup over the leader (C6:D826, template 0x2F, sound 0x12) | H |
| 50 / 51 / 52 | spawn_attr_0 / _2 / _3 | `$0460` attribute bits ORed into spawned actors; visible effect unclear | M |
| 12 | effect_preset | A = preset 0-8 (C2:A81D): effect command list (C2:A42B), objects at `$7E:B073-B872`; `$095D = 3` | M |
| 13 | obj_frame_load | A sheet (C4:0000), `[2]` anim, `[4]` frame, `[6]` OBJ slot 0-8 (VRAM C2:A155): S-DD1 DMA of a 16x16 frame | M |
| 14 | obj_frame_load_wide | as 13 with a wider shape. No site | L |
| 15 | obj_sheet_load | A sheet: slots 0-8 = 3 anims x 3 frames (walk cycle per facing) | M |
| 16 | special | A = sub: 0/1 particles (C2:A2E4), 2 timer `[2]` frames with callback (C2:0AB9 / C2:0AF3), 3 full-screen sequence CC:0570, 4 full-screen setup C0:65D4 (ending) | 2: H, else L |
| 17 / 18 | fx_channel_a / _b | A = handler 1-13 of C2:8ED7, `[2]` `[4]` its parameters: run each field frame (C2:00B8). Handlers not read | H (mechanism) |

## Screen, palettes, VRAM

| N | name | what | |
|---|---|---|---|
| 5 | palette_fade_build | A steps, `[2]` from / `[4]` to palette id (C6:2378), `[6]` `$7F` buffer: blend steps of 0x70 colours (C2:9DBA) | H |
| 6 | palette_fade_build_alt | same into a second set `$04BC-04C0` (who reads it not traced) | M |
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
| 41 | palette_buffer_tint | tint of the palette buffer | M |
| 42 | screen_close_effect_frame | one frame of an HDMA screen-close effect | M |
| 58 | scroll_wave | HDMA raster wave (parameters medium) | H |
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
| 43 / 44 | party_member_set_away / _clear_away | record `+0x01` bit; leave vs reserve unclear | M |
| 57 | party_bond_inc | relationship matrix `$0C38`, each active pair +1, capped at 10 | H |
| 59 | party_remove_member | A = character | H |
| 60 | roster_count | characters in all 8 records → `$0278`. No site | H |
| 61 | party_count_active | battle party size → `$0278` | H |
| 62 | party_get_ids | battle party ids → var.w[0..6] | H |
| 64 | party_damage_all | A = damage, bit 15 lethal | H |
| 70 | inventory_drop_type12 | removes items of categories 1 / 2 (C6:D88B) | M |
| 73 / 74 | party_restore_hp / _mp | battle party HP / MP to max (73 also clears status) | H (73 ✓) |
| 75 | party_add_sp | A added to SP, cap 999 | H |
| 76 / 78 | inventory_stash / _unstash | inventory to / from `$7F:F800`, `$05B8` flag | H |
| 77 | inventory_keep_key_items | removes items of categories other than 1 / 2 (C6:D8C8) | M |
| 79 / 80 | party_solo / party_restore_solo | A alone as leader, others' ids kept at `$03F7`; 80 brings them back | H |
| 81 / 82 | char_restore_hp / _mp | one character | H |
| 84 | get_party_specialty_0a | best level of specialty 0x0A → `$0278` | M |
| 89 | count_ladies_first | members with id in {2, 5, 9, 11, 12} (+ id 1 not leader) → var.w[0], var.w[4] ("Les femmes d'abord", scene 91) | H (code) |
| 90 | party_hp_to_1 | battle party HP to 1 | H ✓ |
| 91 | char_learn | A character, `[2]` spell / skill (`$7E:83E1 + slot * 0x20`) | H |
| 92 | remove_items_1ee_1f1 | items 0x1EE-0x1F1 out of equipment and inventory | H |

## Flags, state, sound

| N | name | what | |
|---|---|---|---|
| 0 | nop | `rts` | H |
| 45 / 46 | sin / cos | A in 2.5° steps (144 a turn) → `$0278`, 256 = 1.0 | H ✓ |
| 47 | sound_source_set_tile | point at tile x, y (x 8) for a distance falloff, maybe volume | L |
| 48 / 49 | walk_slow_on / _off | `$F5` bit 0x40 | M |
| 55 | ambient_event_roll | 25% roll into `$05A4-05A6` if map flag `$0473 & 0x10` | L |
| 56 | set_param_block | var.w[0..10] → `$0501-050B` (read by C2:EA1B, unread). No site | L |
| 66 / 67 | map_flags_set / _clear | `$0439` map property bits. No site | M |
| 69 / 93 | flag2_on / flag2_clear | flag A in `$7E:FE93` (op 5B's flags; C6:E402 / C6:E422) | H |
| 71 | battle_no_game_over | `$02C2` bit 0x20: a party wipe does not end the game | M |
| 72 | keep_sound_on_next_map | `$02C2` bit 7: the next map load skips its music | M |
| 83 | set_var15 | var[0x15] = A unless already 2; 2 blocks a field check (encounters?) | M |
| 85 | sound_signal | releases the sound-sequence player's wait (`$98 = 2`) | M |
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
