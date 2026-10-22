# Old French project (2017–2020)

Source: an archive of the earlier community translation (Manz did its ASM: the old `src/*.s`). Not in the repo.

- Dialog txt per scene block, named by the text pointer (`00E841FC.txt` = scene 4), `[PTn-offset]` sections,
  CP1252. `PTn` drifts in places: the offset / 2 is the message index.
- Generations: `Scripts version 11 2016` → `Tool/StarOcean/INSERT` / `Patch PRE ALPHA/TXT` (2020, latest
  complete, 93/94 scenes; scene 2 is a test message) → `SO-Magno` (2025, 79 files, a half-done reformat with
  broken tags, no new wording).
- Import: `uv run python -m tools.import_legacy "<archive>/Patch PRE ALPHA/TXT"` → `text/fr/scene_NN.xml`.
  Their line breaks are kept as written: katsuji reflow re-wraps paragraphs at build time.

Their tags → ours: `<Pause>` [page], `<End>` [end], `<Speed>`, `<Color>`/`<colour>`, `<Center XXXX>` [pos],
`<Window_style>` [mode8], `<Item>`, `<Image NN01>` [narration]+[page], `<Num>` [var], `<Condition>` [leader],
`<Substring>` [memberD], `<Character NN>` / `[Character NN Name]` name slots; `<Note> <Heart> <Circle> <Male>
<Female> <Star Fill> <Star Empty>` are glyphs (♪ ♥ ○ ♂ ♀ ★ ☆).

Validated on their JP dump: run through the same converter, the control tags match the ROM in all 4012 messages;
line breaks in 3987 (the rest are their dumper's speaker-line quirks, JP only).

Their JP dump also cross-checked our 16×16 table: 22 of our readings corrected (暑 継 菌 東/束 腰 拠 鎖 倒 受 終
祈 歳 疲 臓 恨 讐 鏡 費 薄 検 揺); on the other 44 disagreements their table is wrong (shifted rows, `<術>`-style guesses).

Menus (`tools/import_menus.py` → `text/fr/<db>.xml`):

- `labels8`: `Patch PRE ALPHA/TXT/menu.txt` (SO-Magno's copy of this block is English).
- `names8`, `battle16`, `menu16`: `SO-Magno/SO_items_fra.txt`, blocks `$00` / `$01` / `$03`. Their slot icon codes
  (`<Arme>`...) point at blank tiles and become words.
- Their 8x8 font, recompressed to S-DD1 in its original slot.

Ours, not theirs: item descriptions (translated from the Japanese), full item names (their abbreviations spelled
out), narration / intro / credits graphics. Not used: `SO-Magno/{menu,Battle,description}.txt`.
