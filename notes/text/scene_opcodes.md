# Scene opcodes

Every handler of table C2:3769, by opcode, as `tools.scene_script.OPS` names them. Operands in order; actor n =
record `$7E:2000 + n * 0x40`; tiles are 8 px. Confidence: **H** code read fully, **M** mechanism clear, meaning
partly, **L** guess; **✓** checked in game (warp + injected script). Read by four readers, one range each; the
syscalls (0F) are in `scene_syscalls.md`.

## Flow, variables, flags

| op | name | operands | what | |
|---|---|---|---|---|
| 00 / FF | nop / end | | FF returns from a call or ends the script | H |
| 01 | set | var, expression | RPN expression, store by type (`scene_vm.md`) | H |
| 02 / 03 | inc / dec | var | | H |
| 04 / 05 / 06 | goto / call / ret | jump | | H |
| 07 | if | then, else, condition | | H |
| 13 | wait | frames | yields | H |
| 1A | store_result | sys index | `$0278` to a system variable | H |
| 31 / 32 / 33 | flag_on / off / test | flag | `$7E:FE73` bits | H |
| 5B | flag2_test | flag | `$7E:FE93` bits (chests; syscalls 69 / 93 set / clear) | H |
| 51 | random | mask | `$0278` = random & mask | H ✓ |
| 52 | table_read | table 0-22, index | `$0278` = word of a data table (24-bit pointers at C8:020F; table 0 = characters 0-7) | H ✓ |
| 68 / 69 | array_store / array_load | var, index[, value] | element of a variable, word or byte by its size; load → `$0278` | H ✓ |
| 34 | field_state_get | | `$0278` = `$048A`. No site | M ✓ |
| 09 14 16 1B 23 27 28 3D-42 44 48 50 5C | nop_NN | | bare `rts` | H |

## Text

| op | name | operands | what | |
|---|---|---|---|---|
| 0D | say | message | window by speaker | H |
| 0E / 25 / 39 / 3C | say_mode0 / 1 / 8 / 9 | message | window mode 0 / 1 / 8 / 9 (C2:1C72) | H |
| 30 | choose | first, count | choice window, yields; result to `sys[8]` (`$027A`) | H |
| 4E | wait_text | | re-runs until the window is done | H |

## Actors

Fields: `+0x00` bit 7 active, bit 5 / bit 2 walk in progress / arrived; `+0x01` flags (bit 2 pixel coordinates);
`+0x07` scripted mode (`scene_syscalls.md`); `+0x08` sprite sheet; `+0x09` motion kind (table C6:2E14), saved in
`+0x3A` during a walk; `+0x0A` height; `+0x0E` sprite object; `+0x11` linked actor (emote); `+0x13` / `+0x16`
x / y px; `+0x18` facing (0 up, 1 right, 2 down, 3 left); `+0x24` animation; `+0x35` / `+0x37` walk target.

| op | name | operands | what | |
|---|---|---|---|---|
| 08 | npc_create | n, x, y, facing, sheet, motion, motion param | an actor with a motion kind (wandering NPCs; syscall 28 bounds them) | H (last two M) |
| 2B | actor_create | n, mode, x, y, facing, sheet, `+09`, `+2F`, flags `+01`, `+30`, height, `+0F`, `+04`, flags `+02` | the full creation (facing 4+ sets animation v - 3; `+0F` 4 = random; `+04` also sets speed `+2A`) | H layout ✓, M meanings |
| 0A | chest_create | n, flag2, x, y, item | sprite 0x37, open or shut by the flag2 bit; syscall 11 gives the item | H |
| 10 | actor_walk_to | n, x, y, speed | walk to tile (y stored y * 8 - 16, as op 24); does not wait | H ✓ |
| 11 | actor_walk | n, dir, tiles, speed | walk, facing set; motion 4 until arrival; does not wait | H ✓ |
| 4F | wait_actor_arrive | n | re-runs until `+0x00` bit 2 and position = target; restores `+0x09` | H ✓ |
| 54 | wait_actor_arrive_face | n, facing | the same, then sets the facing | H ✓ |
| 55 | wait_actor_arrive_remove | n | the same, then removes the actor | H |
| 12 | actor_set_anim | n, anim | `+0x24` through C6:56DE; 0 = the facing's default | H (ids M) ✓ |
| 1C | actor_get_facing | n | `$0278` = facing | H ✓ |
| 2F | actor_set | n, offset, value | word for offsets 0A, 13, 16, 2D, 1A-22, else byte; inverse of 35 | H ✓ |
| 35 | actor_get | n, offset | `$0278` = field | H |
| 5D / 5E | actor_field_and / _or | n, offset, mask | byte AND / word OR (also touches offset + 1) | H ✓ |
| 57 / 58 / 59 / 5A | actor_face_up / right / down / left | n | `+0x18` = 0 / 1 / 2 / 3 (1 vs 3 by op 63's convention) | H ✓ |
| 53 | actor_remove | n | off, frees both sprite objects and the linked actor | H ✓ |
| 56 | actor_set_pos | n, x, y | 16 px units. No site | M |
| 61 / 62 | actor_emote / _clear | n, kind / n | icon above the actor (C2:324D, table C2:3292; 1 anger, 2 ?, 3 !, 9 sweat), slot in `+0x11`; 62 removes it but leaves `+0x11` | H ✓ |

## Triggers and tiles

Map tiles: attribute grid `$7E:EE73 + y * [$0307] + x` (`$0307` / `$0308` map width / height), bit 7 = trigger
mark. Entry pointers and the trigger lists share the block cleared at scene load (`scene_triggers.md`).

| op | name | operands | what | |
|---|---|---|---|---|
| 21 | trigger_tile | x, y, entry | 3-byte entry at `$EA13 + [$023F]`: the hero stepping on it calls entry (2, id) | H ✓ |
| 22 | trigger_zone | x1, y1, x2, y2, entry | 5-byte box at `$EB93 + [$0241]`, inclusive: same | H ✓ |
| 36 / 37 | trigger_tile_off / trigger_zone_off | x, y / box | id = FF (marks stay); 37 often opens the zone's own script | H ✓ |
| 0B | actor_trigger_tile | x, y, entry | list `$E913` (end `$023B`): an actor stepping on it runs entry (1, id) with the actor in `$0278` (C6:535B) | H |
| 0C | actor_trigger_rect | x1, y1, x2, y2, entry | list `$E973` (end `$023D`): same (C6:5446) | H |
| 5F / 60 | actor_trigger_tile_off / _rect_off | x, y / box | id = FF | H |
| 3A / 3B | tile_attr_set / tile_attr_fill | x, y / box, attr | low 7 bits of the attribute; scripts use 0 / 64 next to obstacles, probably passability | H ✓ (meaning L) |
| 1F / 20 | bg_tile_set / bg_tile_fill | bg, x, y / box, pattern | BG1-3 tile patch (patterns C6:1D51), logged at `$EE13` (end `$0243`); waits while `$0433 & 3`, yields 1 frame | H (mechanism) |

## Map, camera, screen

| op | name | operands | what | |
|---|---|---|---|---|
| 24 | map_change | map, kind, x, y, facing | kind 0 (and 3+) fade 16 frames, 1 no fade (after the script's own), 2 door: opening-door actor (C6:E18F) and sound `$0446` (`scene_triggers.md`) | H (1 / 2 M) |
| 26 | map_change_continue | map, kind, x, y | as 24, the script resumes after the load; `$F5` bit 4. One site | M |
| 29 | camera_pan_to | tile x, tile y, speed | target (t - 14) * 8 px clamped; 8.8 px / frame; moves only after 2D | H ✓ |
| 63 | camera_pan_by | dir, tiles, speed | by tiles * 8 px; neither waits (`$024D` frames left) | H ✓ |
| 2A | camera_pan_axis | tile x, tile y, speed | one axis. No site | L |
| 2D / 2E | cutscene_begin / cutscene_end | | player control off / back (`$F5` bit 1, saved `$02DE`), `$05BC`; 2E waits out an item popup | H ✓ |
| 1E | fade | kind, speed | 0 in / 1 out (brightness, C8:0922, `$049D-04A4`), 4 mosaic in / 5+ out (C8:0674, `$04A6-04AD`); 2-3 rate only; rate speed * 16 | H ✓ |
| 4D | cgram_set_color | index, BGR15 | through an NMI job (`$F4` bit 7), 1 frame | H ✓ |

## Sound

| op | name | operands | what | |
|---|---|---|---|---|
| 17 | music_play | song, p2, p3 | skipped if playing (C4:F58B), else C0:85FE | M |
| 18 | music_fade_out | v | APU command 8 | M |
| 19 | sound_command | cmd, p1, p2, p3 | raw APU command (C0:8594, `$4C-4E`); 0x17 saves the field song in `$02DA` | M |
| 38 | sfx_play | id, pan | pan 64 centre, FF by the leader's screen x, FE random; also sets bit id in SRAM `$70:7E0D` (sound test?) | H |
| 1D | sound_source_set | x, y, unused | `$0516 / $0518`, as syscall 47 | H |

## Party, items, menus

Characters are passed as id - 1, except 4B / 4C (id from 1; `op_4b 0, 0` in scene 7 finds nothing).

| op | name | operands | what | |
|---|---|---|---|---|
| 2C | item_add | item, count | as syscall 11, sets count bit 6; scene 1's starting items | H ✓ |
| 45 | item_count | item | `$0278` | H ✓ |
| 46 | party_join | char | back from away, or a new record, moved forward | H |
| 47 | party_leave | char | equipment `+0xA6 / +0xA8` to inventory, away bit, record to the end | M |
| 49 | char_party_pos | char | `$0278` = 1-4 battle slot, 5-8 reserve, 0 absent or away | H ✓ |
| 4A | char_order_index | char, unused | computes, stores nothing. No site | H |
| 4B / 4C | char_unequip / char_equip_get | char, slot 0-6 | 4C → `$0278`, no site | H (4C ✓) |
| 64 / 65 | bond_modify / bond_get | a, b[, mode, amount] | `$0C38[a + b * 16]`: mode 0 + (cap 10), 1 - (floor 0), 2+ set; get → `$0278` | H ✓ |
| 66 / 67 | char_table_get / _set | char, offset[, value] | low nibble of `$84E1 + k * 0x40 + offset` (CC:0092), maybe skill levels | M |
| 43 | open_shop | shop 1-34, 0 | `$02E8` bit 1, the field opens menu 0x0B with `$077A` = shop | H ✓ |
| 15 | battle_start | formation, param | `$0963`, `$0B8C`, `$02C2` bits; leaves the VM (between `sound_command 23` and `10`) | M |
