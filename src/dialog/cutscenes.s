"""
Intro subtitles and credits drawn as sprites (C3:8ECB frames): tools/cutscene_text.py renders the French lines
(text/fr/cutscenes.toml) as S-DD1 cels in text16 and writes cutscenes.i: the frames, in the bank CC pool made of the
Japanese frames and the padding before the bank end, and the sprite-list words repointed to them. The credit
titles on BG3 (C2:DB33) are 256x16 2bpp streams the credits script at C2:DA57 names: their operands are repointed.
"""

.import "core/preamble"
.import "menu/text16"

.include "cutscenes.i"
