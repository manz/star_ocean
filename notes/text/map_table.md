# Map table and the map → scene link

## Map records (FF:C800)

- `FF:C800`: one LZ block (`C0:4C53`), unpacked to `$7F:0000` by `C6:2093` on every map load. 0x30-byte records by
  map id; `C6:20AB` copies record `$043D * 0x30` to `$7E:8743`.
- 682 slots, 608 with a scene (the rest are 0: unused ids).
- `+0x21`: the map's scene (1-94). Other fields not mapped yet (encounter rate `$0287`, backdrop `$028C`, map flags
  `$0439` are candidates).

## Scene switch (C6:10CA)

Scene = `$7E:8764` (record +0x21). If it differs from `$0232` (the loaded scene), `C6:10E3` reads the event pointer
at `E4:(scene - 1) * 6` and unpacks it to `$7E:3100`; then `C2:36A9` resets the VM and the scene's start-up runs
(`scene_triggers.md`). Maps of the same scene keep the event data: a warp between them does not unpack.

## Story graph from the scripts

A scene's setup branches on `sys.w[0xc] == map` and places that map's triggers (`trigger_tile` / `_zone`, NPCs,
chests); entries then do `map_change`, flags, story vars, battles, shops. Walking each setup with the map id as a
symbol, other conditions kept as guards:

- 535 maps named in setups; all but three agree with the record's scene: 548 (tested by scene 83, record 88), 559
  (91, record 90), 578 (90, record 93).
- The other 73 maps of the table belong to scenes whose setup does not test the map (one-map scenes, e.g. scene 4).
- 1490 exits (trigger box → map, x, y, facing) from 547 maps, all to maps of the table, each with the guards it
  needs (`var.w[0x10]` story progress, `var.w[0x38]`, ...). 59 maps have no exit and are no exit's destination.
- Guards are what every path to an instruction took (a data flow keeping their intersection): the conditions that
  must hold, not one path's history. A scene with independent `if`s would otherwise multiply its paths.
- Map 22's north zone (entry 2) only pushes the hero back: no exit, and none in the graph.

`uv run python -m tools.story_graph [MAP ...]` (`tools/map_table.py` for the records).

## Story counter `var.w[0x10]`

- Only goes up over the game: 12 at the start save, then 43, 55, 64, 93, 102, 125, 133, 142, 155, 171, 173 over
  fantasyanime's twelve slots (Seven Star Ruins). The scene flags `$FE73` grow with it.
- Its writes (`inc`, `set =`, `set +=`) are the story's steps: `--story [V ...]` lists them with the value(s) their
  guards allow (any comparison, `&&` / `||`, negated on the else side; pinned when 8 values or fewer remain), the
  map and what fires them (arrival setup, trigger zone, talking to an actor). Guards that contradict (one placement of
  an actor with the entry path of another) are dropped.
- Every value from 12 to 173 has a step out of it, or a jump over it (`set` to a later value), except 59, 109, 110,
  143, 144, 149. 109: scene 48's zone 65 (placed at 109) runs a cutscene that never writes the counter; something
  else moves it (a syscall or an indirect write?). Open.
- Every save slot's value has a next step (`tests/test_story_graph.py`).
- Scene 1 (map 0) is a chapter select that sets the counter to dozens of values: not a story step, a start.

## Save slot layout (C2:D119)

Records of (count, WRAM address), read in order from slot + 0x25C by the loader `C2:D53E`: map `$043D` (+0x271),
hero position (`$2013`, `$2016`, facing), Fol, then flags `$FE73` (32 bytes, +0x2AD), chest flags `$FE93` (48),
variables from `var.w[0x10]` (`$FED3`, 56 bytes, +0x2FD). `tools/save_slot.py`.
