# Text

Dump everything: `uv run python -m tools.dump_text` → `text/jp/scene_NN.xml` (dialog, pointer id = message
index) and `text/jp/{names8,labels8,battle16,menu16}.xml` (pointer id = game string id, one per distinct
string). snes.ninja ScriptNS, encoded/decoded with a816's `script.Table`; `tests/test_text.py` re-encodes
every file back to the ROM bytes.

| file | what |
|---|---|
| `dialog.md` | scene table, block layout, control codes |
| `strings.md` | the four id-indexed string databases (menus, names, battle) |
| `tables.md` | glyph / control tables, confidence |
| `legacy.md` | old French project: versions, tag mapping, import |
| `puzzles.md` | word puzzles: scene 80 console, event-data edits |
| `scene_vm.md` | scene event VM: dispatcher, operands, `tools.scene_script` |
