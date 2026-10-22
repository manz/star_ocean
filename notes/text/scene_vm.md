# Scene event VM

`uv run python -m tools.scene_script NN [--edited] [--bytes]` lists scene NN's event data, with the French first
line next to each message. The module docstring has the byte formats. `tools.scene_asm` encodes the same structures
back (every scene re-encodes to its own bytes) and assembles scripts with labels from Python. Header, triggers and
map changes: `scene_triggers.md`.

## Storage

- Scene record +0 (table `$E4:0000`, `tools.dialog.SCENE_TABLE`): 24-bit pointer to the LZ container (0x81/0x83),
  unpacked by the game's `unpack` (C0:4C53) to `$7E:3100`.
- That `unpack` reads the plain bus: event data must stay in the banks it maps, never in ROM pages 6-7 (the
  `rom_pages_67` pool). Scene text can go there only because `text_unpack_sram` switches the E window first. An
  edited block is written over the original (`tools.scene_events`), so it must pack no bigger.

## Running

- Dispatchers: C2:1258 / C2:1271 per frame, until a yielding opcode; C2:1288 / C2:1297 run until an FF (used for
  trigger scripts that must finish at once). `$0231` negative skips the VM.
- pc `$0238` (absolute, `$3100 + offset`), frame countdown `$0234`, `$023A` cleared before each opcode. Call stack
  grows down from `($FE)` (`$FFF2` at scene load).
- Opcode table C2:3769, indexed by (opcode + 1) * 2: 00-69 and FF.
- Jump / call words count from the header's end: target = `$3100 + [$3100] + word`. `04` goto, `05` call, `06` ret,
  `FF` end (returns from a call, or ends the script).

## Operands

- Value (C2:310C), by its first byte `t`: F0-FF a run (the next `t & 0x0F` values are bare bytes; the count lasts
  the instruction); bit 7 a variable, `$7E:FEC3 + index`, with bit 6 the system table C2:383F (24-bit pointers),
  index one byte or two (15 bits, first byte has bit 7), size `t & 3`; else an immediate of `(t & 3) + 1` bytes.
  The game does not always pick the smallest width (scene 80 `0xca` holds 255 as a word): `Value` keeps the width.
- `sys.w[0xc]` is the map id (the map loader keeps the current one at `$7E:043D`; that they are the same word is
  not checked). `var.w[0x10]` reads as story progress (scene 80: 143, 144, 145).
- Result register `$0278`: set by `actor_get`, `flag_test` and others, written out by `store_result`.
- `set` (01): a variable then an RPN expression up to FF, on a stack that starts with the variable's value
  (C2:12CA). A token with `& 0x3C == 0` is a value, else an operator (C2:16A7 byte / C2:16B9 word): 04 +, 05 -,
  06 *, 07 /, 08 |, 09 &, 0A ++, 0B --, 0C drop. The variable type's bits 3-5 pick the store (C2:16DD): = += -= *=
  /= |= &= ?=.
- `if` (07): then word, else word, condition list (C2:17C9): comparator (C2:18FE: 0 ==, 1 >, 2 <, 3 !=, 4 >=, 5 <=,
  6 one value truthy), its values, joiner (C2:17F7: 00 or, 01 and, FF end).

## Opcodes read so far

| op | name | what |
|---|---|---|
| 0D | say | message (1-2 byte index), window by speaker |
| 0F | syscall | N: service N (0-93) of the table at C2:8B4C, A = `var.w[0]`, arguments in `var.w[2..]`; result in `$0278` |
| 0E / 25 / 39 / 3C | say_mode0/1/8/9 | message in window mode 0 / 1 / 8 / 9 (C2:1C72) |
| 13 | wait | yield V frames |
| 1A | store_result | `$0278` to a system variable |
| 24 | (map change) | map, kind, x, y, facing: `scene_triggers.md` |
| 30 | choose | choice window, yields; result to `sys[8]` |
| 31 / 32 / 33 | flag_on / off / test | flags at `$7E:FE73` |
| 35 | actor_get | actor field to `$0278` |
| 4E | wait_text | re-runs until the window is done |
| 5B | flag2_test | flags at `$7E:FE93` |

Messages: the scene text table at `$B873` (`sram_text.s` copies the selected one there); message index m is XML id
m (checked in game on scene 80's reveal). The other `op_NN` have their operand layout read from the handler, not
their effect.

## Checked

All 94 scenes sweep clean (scenes 2, 52, 76 end in one stray 0x80) and re-encode to their bytes; 28k traced
instructions from five saves land on instruction starts with the expected lengths.
