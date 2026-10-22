"""
The yes / no choice bubbles (the C4:2409 and C4:2457 sprite frames, "はい" / "いいえ"): tools/yes_no.py redraws them as
"Oui" / "Non" and writes yes_no.i: every cel's streams in text16 and the frames' sources repointed to them.
"""

.import "core/preamble"
.import "menu/text16"

.include "yes_no.i"
