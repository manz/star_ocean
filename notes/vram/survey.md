# VRAM survey

| screen | mode | text layer | free 2bpp tiles in the text CHR window |
|---|---|---|---|
| field | 1 + BG3 prio | BG3 chr `$4000`, map `$7400` | `$5940-$5FBF` (208, idle dialog buffer), `$53F0-$54FF` (34) |
| dialog | 1 + BG3 prio | BG3 chr `$4000`, map `$5800` | `$5990-$5ADF` (42), `$5C60-$5FBF` (108) |
| menu | 0 | BG4 chr `$4000` map `$5800`; BG1-3 chr `$2000` | `$48C0-$4BFF` (104), `$5520-$595F` (136), `$5A20-$5FBF` (180) |

Free = all-zero CHR runs at capture time; recheck per screen before claiming a pool.
Battle not surveyed yet.

## Menu BG1-3 window (chr `$2000`, tiles 0x000-0x3FF), what writes it

Random menu tours (3 seeds x 600 presses, DMAs to `$2118` while BGMODE = 0):

| tiles | source | content |
|---|---|---|
| `000-0BF` | `DB:A078` (S-DD1, 0xC00) | 8x8 font, reloaded on every menu open |
| `0C0-0CE` | `FE:539D` | window frame pieces |
| `0D0-0D8` | `FE:5CCE` | pre-drawn pieces (status labels) |
| `0CF`, `0D9-113` | nothing | free (60 tiles) |
| `114-3F3` | `$7F:0000` | 16x16 VWF columns (tile 0x114 + `$DD`): one tour reached 0x3F3 |

Everything above 0x113 not written on a given screen holds stale field CHR. An 8x8 VWF pool can only come from
the font's own 192 tiles (minus the fixed ones the code prints) and the 60 free ones, unless the 16x16 pool is
capped.
