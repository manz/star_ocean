"""
Title menu (New Game / Continue / Sound Player): sprite frames of cels in the title sprite sheet (DA:F458, tiles
0x100-0x1DF). tools/title_menu.py draws the French items over the Japanese ones' tiles and writes title_menu.i: the
sheet in text16 (CC:2441 repointed), the frames in the bank CC pool cutscenes declares, the sprite-list words.
"""

.import "core/preamble"
.import "menu/text16"
.import "dialog/cutscenes"

.include "title_menu.i"
