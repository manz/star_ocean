# Battle text layer

- BG mode 1, BG3 priority. BG3 = the windows: 2bpp, chr word `$4000`, map `$5C00` (32x32), DMA'd from the
  shadows `$7E:5100` / `$7E:5900` by the line-216 IRQ list. BG1 map `$5400`, BG2 `$5800`, BG1/2 chr `$0000`.
- BG3 tiles `280+` are the BG1-3 maps: the text CHR window is tiles `000-27F`.
- Tiles the map reads in a fight (3 states x 3 seeds, random presses until the fight ends): `000-0BF` (menu font,
  borders `B4-BF`) and `114-13B` (16x16 message, uploaded by `C0:0188`). Blanking `C0-113` or `13C-27F` changes no
  frame while `$02C2` bit 0 is set.
- `C0-EF` hold field leftovers ("Attaque / Esquive / Défense", window pieces), never drawn in a fight. `200-27F`
  is filled by `C6:0B5D...` after the fight.

## Writers (fixed font into the shadows)

| routine | draws | callers |
|---|---|---|
| `C0:3FA3` | names8 by id (`C0:3FF7` stores) | `C1:5619`/`C1:56E3` party window, `C1:578A`, `C1:4700` enemy names |
| `C0:4154` | 8x8 string at A:Y (copy of `CA:BCAD`), X = map offset, `$06` palette | `C1:2EDD` item list (`C1:2FB8`, 8 cells), `C1:539F`, `C1:5473`, `C3:0DFE`, `C9:0278` |
| `C0:4501` | numbers (digits `10-19`), blank `BF` | party PV/PM, item counts |

- Item list: `C8:1050` (from `C1:0006`, fight start) fills `$7E:A353` with each inventory slot's names8 string
  (offset list `D7:0000` from id `0x1388`). A savestate keeps the table of the build it was made on: an older
  names8 layout shows strings cut at the start ("ing" for "Stylo d'étude"). Not a patch bug; refresh the states.
- The list draws 8 cells a name: French names past 8 letters are cut ("Artisana").
