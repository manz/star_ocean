# Message annotations

`uv run python -m tools.annotate` writes, on every `<sn:pointer>` of `text/fr` and `text/jp/scene_NN.xml`, how
the event scripts (with `tools.scene_events` edits) use the message. Rerun it after a script edit or a fresh
`tools.dump_text`; `tests/test_annotate.py` fails while a file is stale.

| attribute | from |
|---|---|
| `choice` | the last `say` before a `choose` (op 30) with no `end` / `ret` between: the option count, `yes-no` for 0, `dynamic` for a variable count or one that differs between sites |
| `window` | the `say` ops naming it: `speaker` (op 0D) or `say_modeN`'s N |
| `trigger` | the header entries whose walk reaches it (`scene_triggers.md`): `start`, `talk N`, `search` (2/0x7F), `touch` (2/0x7D), `tile N`, `actor N` |
| `unused="1"` | no reached `say` names it (55 per language, e.g. scene 44 message 136) |

`tools.encode_text` fails the build when a `choice="N"` message has numbered lines (`1. `) that are not N, one
the reflow would join to the next (no `[br]`), or one wider than the window. Menus with no numbered lines are built
elsewhere: scene 13's elevator (count 1), scene 80's console and scene 85's `[leader]` menu (`dynamic`, one message
per option line).
