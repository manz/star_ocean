# Battle text layer

- BG mode 1, BG3 priority. BG3 = the windows: 2bpp, chr word `$4000`, map `$5C00` (32x32), DMA'd from the
  shadows `$7E:5100` / `$7E:5900` by the line-216 IRQ list. BG1 map `$5400`, BG2 `$5800`, BG1/2 chr `$0000`.
- BG3 tiles `280+` are the BG1-3 maps: the text CHR window is tiles `000-27F`.
- Tiles the map reads in a fight (3 states x 3 seeds, random presses until the fight ends): `000-0BF` (menu font,
  borders `B4-BF`) and `114-13B` (16x16 message, uploaded by `C0:0188`). Blanking `C0-113` or `13C-27F` changes no
  frame while `$02C2` bit 0 is set. Those runs never showed a long help line: the item list's ("Restaure les PV des
  alliés proches") goes to `13F`, and the line's 28 columns (2 tiles each from `114`) can reach `14B`.
- `C0-EF` hold field leftovers ("Attaque / Esquive / Défense", window pieces), never drawn in a fight. `200-27F`
  is filled by `C6:0B5D...` after the fight.

## Windows (src/battle/windows.s)

- `C1:527D` frames three windows at the top (X = 0) or the bottom (X = 0x540, the command ring open): enemy names,
  the party member (name, PV, PM), the L/R special moves. The patch makes them 11 / 11 / 12 wide at cells 0 / 10 / 20
  (were 12 / 11 / 11 at 0 / 11 / 21): a special move's name gets 10 cells (21-30, under
  the L / R labels). `C1:521B` frames the full-width
  party window (4 members, PV / PM rows from `C1:5402` / `C1:5842`), untouched.
- The bottom copy of the party member window (`C1:5557`) put the name and PV one cell right of the top's and drew PV
  with 3 digits: 6746 showed as 746. The patch draws it as the top one.

## Writers (fixed font into the shadows)

| routine | draws | callers |
|---|---|---|
| `C0:3FA3` | names8 by id (`C0:3FF7` stores) | `C1:5619`/`C1:56E3` party window, `C1:578A`, `C1:4700` enemy names |
| `C0:4154` | 8x8 string at A:Y (copy of `CA:BCAD`), X = map offset, `$06` palette | `C1:2EDD` item list (`C1:2FB8`, 8 cells), `C1:539F`, `C1:5473`, `C3:0DFE`, `C9:0278` |
| `C0:4501` | numbers (digits `10-19`), blank `BF` | party PV/PM, item counts |

- Item list: `C8:1050` (from `C1:0006`, fight start) fills `$7E:A353` with each inventory slot's names8 string
  (offset list `D7:0000` from id `0x1388`). A savestate keeps the table of the build it was made on: an older
  names8 layout shows strings cut at the start ("ing" for "Stylo d'étude"). Not a patch bug; refresh the states.
- Laid out as the field's Bagage (src/battle/items.s): columns 16 cells apart, not 14, the second one's icon, name,
  `:` and count at cells 18 / 19 / 27 / 28-29; the hand's x follows (`C1:330E`).
- The list gives a name 8 cells (`C1:2FA7`): the `:` before the count is drawn at cell 9 (`X + 0x12`) and covers what
  ran past. `C0:4154` has no limit of its own. With BATTLE_VWF8 a name takes its inked tiles, not its codes: of 696
  names8 strings from `0x1388`, 22 run past 8 cells, monster names but one ("Épée longue+2", 9); the list stays as is.

## 8x8 VWF in battle (BATTLE_VWF8, src/battle/vwf8.s)

- `C0:3FA3` (names8 by id) and `C0:4154` (string at A:Y) draw strings that have a vwf8 record from the shared pool:
  tiles `0D9-113` and `14C-1FF` of BG3 CHR `$4000`, written into both shadows. Party nicknames (`$7E:7497`, $100
  apart) come from the runtime pen (notes/vram/pen8.md); numbers stay on the fixed font.
- The fight start (`C1:0006`) opens the battle pool, its end (`C0:20F7`) the menus' again; a string drawn first in
  a savestate taken mid-fight opens it too.
- Uploads: the line-216 IRQ's DMA list end (`C0:0188`, its V-blank wait) runs the S-DD1 streams on channel 1 with
  the E / F windows on pages 2 / 3, until line 250 (the audio IRQ at 258); what is left waits a frame. The drain
  trusts the ring only while the battle pool is open and each slot targets the battle CHR (the state is in SRAM:
  a cold boot or another build leaves bytes there).
- Cost (`battle_chest` / `battle_busy`, 600 frames): 0.3% / 1.2% of a frame on average. `tools.battle_bench`
  step counts are not comparable across builds: the fights' RNG follows the timing and the fights diverge.
