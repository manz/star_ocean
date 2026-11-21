# Game modes (what a bot reads to know where it is)

No single mode byte: the field loop runs everything, battle and menu included.

## Structure

- Reset `00:FEC1` → `jmp C0:8001` (`main_entry`). NMI `00:FEB9` → `C0:0000` is a bare `rti`; the game runs on the
  IRQ (`00:FEBD` → `C0:0221`).
- `C2:0000` `field_main_loop`: one frame = about 35 subsystems called in order (`C2:1258` scene VM, `C6:2D45` field
  actors, `C2:6A21` battle step, `CB:0000` menu step, `C2:38AB` dialog task, ...), then `C2:0B5E` (NMI jobs), `jmp`
  back. Each subsystem checks its own flags.
- Battle: `C2:6A21` → `C0:20EA` → `jsl C1:0000`. The whole battle is a subroutine of one field frame; the field loop
  resumes after it.
- Menu: `CB:0000` opens it when `$02E8` is set, from inside the field loop.
- Title: `CC:278C` → `C0:5193`, outside the field loop.

## Mode from RAM (checked on tests/states and a fantasyanime save)

Test in this order:

| mode | test | notes |
|---|---|---|
| title / load | `$2000` (hero record) = 0 | weak: needs a real title flag |
| battle | `$02C2` bit 0 | bit 1 = encounter requested (swirl); bits cleared back in the field |
| menu | `$02E8` bit 7 | `$02E8` ≠ 0 asks for it; bit 1 = shop (`$077A` shop id) |
| choice | `$0258` bit 7 | op 30; cursor `$025E` (1-based: 1 Oui, 2 Non), answer `$027A` (sys[8]) after A; `$0231` bit 7 (VM paused) while open |
| dialog | `$F5` bit 3 | set by the say ops (`C2:1C72`), with `$048A` bit 5; text cursor `$03D5` |
| event | `$F5` bit 1 | player has no control; menu and battle set it too, so test it after them |
| field | otherwise | |

Field subsystems refuse to start (no encounter, no menu) while any of these is set: `$0431` ≥ 2, `$05BB`, `$04A6`,
`$049D`, `$0468` (word), hero `$2000` bit 6. A bot that wants to open the menu or walk into a fight waits for all of
them to clear.

## Encounter roll

`C2:6F20` (`C2:7029` the `var[0x15]` test): carry set = fight. It sets `$02C2` bit 1, clears `$02E8`, `$05A4`,
sets `$0963` (formation) and `$0B8C` = `$028C` (backdrop). `C2:6A21` then runs the swirl (`$02C5` += 4 a frame to
0x90) and calls the battle.

## Open

- A real title / boot flag.
- `$F5` bit 3 clearing: seen cleared after the yes/no; check a plain message closing.
- Battle internals: outcome, defeat, control (see notes/engine/battle_timing.md for the loop).
