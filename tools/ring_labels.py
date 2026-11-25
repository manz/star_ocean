"""The fight's command ring labels in French: SPECIAL, ITEM, RUN, TACTICS and CHANGE redrawn as SPÉCIAL, OBJET, FUIR,
TACTIQUE and ÉCHANGE, written to ring_labels.bin for src/battle/ring_labels.s.

The ring shows the picked command's label as a sprite frame of the C3:8ECB format (C1:4F50 holds the five frame
pointers): a 3-byte header, then one 8-byte record per 8x8 cel (size 0, dx, dy, a 24-bit source), each cel one
0x20-byte S-DD1 stream. The labels are capitals 6 rows high, colour 15 ink with a colour 1 outline; the French ones
keep each frame's cel count (32, 24 or 16 px). Every cel's stream goes in its own 0x40-byte slot of the blob, so cel n
sits at ring_labels + 0x40 * n, in frame order.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from tools import obj_letters as letters
from tools import sdd1
from tools.rom import ROOT

OUT = ROOT / "build" / "gen" / "ring_labels.bin"
CEL = 0x20  # an 8x8 4bpp tile
SLOT = 0x40
INK = 15
RECORD = 8

# fmt: off
GLYPHS: letters.Glyphs = {  # rows 1-6, as the game's own labels draw them; B F J O Q É drawn alike
    "A": (".#.", "#.#", "#.#", "###", "#.#", "#.#"),
    "B": ("##.", "#.#", "##.", "#.#", "#.#", "##."),
    "C": (".##", "#..", "#..", "#..", "#..", ".##"),
    "E": ("###", "#..", "##.", "#..", "#..", "###"),
    "É": ("..#", "###", "#..", "##.", "#..", "#..", "###"),  # the accent on row 0
    "F": ("###", "#..", "##.", "#..", "#..", "#.."),
    "G": (".##.", "#..#", "#...", "#.##", "#..#", ".###"),
    "H": ("#.#", "#.#", "###", "#.#", "#.#", "#.#"),
    "I": ("#", "#", "#", "#", "#", "#"),
    "J": ("..#", "..#", "..#", "..#", "#.#", ".#."),
    "L": ("#..", "#..", "#..", "#..", "#..", "###"),
    "N": ("#..#", "##.#", "##.#", "#.##", "#.##", "#..#"),
    "O": (".#.", "#.#", "#.#", "#.#", "#.#", ".#."),
    "P": ("##.", "#.#", "#.#", "##.", "#..", "#.."),
    "Q": (".#.", "#.#", "#.#", "#.#", "#.#", ".##"),
    "R": ("##.", "#.#", "##.", "#.#", "#.#", "#.#"),
    "S": (".##", "#..", ".#.", "..#", "..#", "##."),
    "T": ("###", ".#.", ".#.", ".#.", ".#.", ".#."),
    "U": ("#.#", "#.#", "#.#", "#.#", "#.#", ".#."),
}
# fmt: on


@dataclass(frozen=True)
class Label:
    frame: int  # bus address of the sprite frame
    cels: int
    text: str

    def source(self, cel: int) -> int:
        """Bus address of the cel record's 24-bit source."""
        return self.frame + 3 + cel * RECORD + 5


LABELS = (
    Label(0xC15052, 4, "SPÉCIAL"),
    Label(0xC15075, 3, "OBJET"),
    Label(0xC15090, 2, "FUIR"),
    Label(0xC150A3, 4, "TACTIQUE"),
    Label(0xC150C6, 4, "ÉCHANGE"),
)


def tiles(label: Label) -> list[bytes]:
    """The label's cels, left to right."""
    grid = letters.paint(label.text, GLYPHS, label.cels * 8, INK, INK)
    out = []
    for cel in range(label.cels):
        tile = bytearray(CEL)
        for y, row in enumerate(grid):
            for x in range(8):
                letters.put(tile, 0, x, y, row[cel * 8 + x])
        out.append(bytes(tile))
    return out


def blob() -> bytes:
    out = bytearray()
    for label in LABELS:
        for tile in tiles(label):
            packed = sdd1.compress(tile)
            if len(packed) > SLOT:
                raise ValueError(f"{label.text!r}: a cel packs to {len(packed)} bytes, a slot holds {SLOT}")
            out += packed + bytes(SLOT - len(packed))
    return bytes(out)


def build(out: Path = OUT) -> int:
    data = blob()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return len(data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    print(f"{build(ap.parse_args().out)} bytes")


if __name__ == "__main__":
    main()
