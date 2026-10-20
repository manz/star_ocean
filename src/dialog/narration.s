"""
Narration screens: the Kurt letter and the Calnus intro are pre-rendered 208x16 line pictures, S-DD1 streams read
through the table at `C2:681A` (13 screens x four 3-byte line pointers, palette pointer, pad). tools/narration.py
renders the French lines (text/fr/narration.toml) and writes narration.i: one alloc per line and the table pointer
to it. The lines go in text16 (menu/text16: freed Japanese text, banks E4-FF, which the S-DD1 reads as well), to
which this module adds the Japanese line streams.
"""

.import "core/preamble"

; The Japanese line streams, then the 0xFF padding before the FE and FF bank ends.
.pool text16 {
    range 0xFC312A 0xFC32B3
    range 0xFC1043 0xFC11DE
    range 0xFC9CB8 0xFC9E09
    range 0xFCD9EA 0xFCDB24
    range 0xFD2BCB 0xFD2DC8
    range 0xFC59D2 0xFC5B4B
    range 0xFCE004 0xFCE13A
    range 0xFC832D 0xFC848C
    range 0xFDAFCB 0xFDB064
    range 0xFD7D39 0xFD7E17
    range 0xFDE3D8 0xFDE439
    range 0xFD3A49 0xFD3B36
    range 0xFCC604 0xFCC744
    range 0xFDDC40 0xFDDCAA
    range 0xFDA8DF 0xFDA984
    range 0xFCF8EB 0xFCFA12
    range 0xF6FF1A 0xF6FFFC
    range 0xFD9856 0xFD9912
    range 0xFEFE0B 0xFEFFFF
    range 0xFFFE54 0xFFFFFF
    strategy pack
}

.include "narration.i"
