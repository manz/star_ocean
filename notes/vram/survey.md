# VRAM survey

| screen | mode | text layer | free 2bpp tiles in the text CHR window |
|---|---|---|---|
| field | 1 + BG3 prio | BG3 chr `$4000`, map `$7400` | `$5940-$5FBF` (208, idle dialog buffer), `$53F0-$54FF` (34) |
| dialog | 1 + BG3 prio | BG3 chr `$4000`, map `$5800` | `$5990-$5ADF` (42), `$5C60-$5FBF` (108) |
| menu | 0 | BG4 chr `$4000` map `$5800`; BG1-3 chr `$2000` | `$48C0-$4BFF` (104), `$5520-$595F` (136), `$5A20-$5FBF` (180) |

Free = all-zero CHR runs at capture time; recheck per screen before claiming a pool.
Battle not surveyed yet.
