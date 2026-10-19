"""
Names (names8: party, items, skills, spells, enemies): French strings in place of the Japanese and of battle16's
(moved to the text16 pool), offset list D7:0000 rewritten (build/gen/names8.i, tools/encode_menus.py). C0:4B60
(build/gen/glyph_map.i) turns their 8x8 codes into 16x16 / dialog glyphs for the item panel and [item] inserts.
"""

.include "names8.i"
.include "glyph_map.i"
