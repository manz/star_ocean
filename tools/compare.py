"""Japanese and French side by side, matched by id: a scene's messages or a database's strings.

python -m tools.compare 22                 # every message of scene 22
python -m tools.compare 22 94-99 108       # some messages
python -m tools.compare 22 -g バダム        # messages whose Japanese or French matches
python -m tools.compare menu16 0xFB90-0xFB9E
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from tools.rom import ROOT

TEXT = ROOT / "text"
ENTRY = re.compile(r'<sn:(?:pointer|string) id="(0x[0-9A-Fa-f]+|\d+)">(.*?)</sn:(?:pointer|string)>', re.DOTALL)
END = "[end]"


@dataclass(frozen=True)
class Pair:
    id: int
    jp: str
    fr: str


def entries(path: Path) -> dict[int, str]:
    """id -> text, the trailing [end] and newlines dropped; an absent file reads empty."""
    if not path.exists():
        return {}
    return {
        int(m[1], 0): m[2].rstrip("\n").removesuffix(END).rstrip("\n")
        for m in ENTRY.finditer(path.read_text(encoding="utf-8"))
    }


def source(name: str) -> str:
    """A scene number -> its file name (scene_NN), anything else is a database name."""
    return f"scene_{int(name):02d}" if name.isdigit() else name


def pairs(name: str, root: Path = TEXT) -> list[Pair]:
    jp, fr = entries(root / "jp" / f"{name}.xml"), entries(root / "fr" / f"{name}.xml")
    return [Pair(i, jp.get(i, ""), fr.get(i, "")) for i in sorted(jp.keys() | fr.keys())]


def parse_ids(specs: list[str]) -> set[int]:
    """'94', '94-99', '0xFB90-0xFB9E' -> the ids they name."""
    ids: set[int] = set()
    for spec in specs:
        first, _, last = spec.partition("-")
        ids.update(range(int(first, 0), int(last or first, 0) + 1))
    return ids


def select(rows: list[Pair], ids: set[int], pattern: str | None) -> list[Pair]:
    found = re.compile(pattern) if pattern else None
    return [
        row
        for row in rows
        if (not ids or row.id in ids) and (found is None or found.search(row.jp) or found.search(row.fr))
    ]


def render(row: Pair, hexadecimal: bool) -> str:
    label = f"0x{row.id:04X}" if hexadecimal else str(row.id)
    return (
        f"=== {label}\nJP: {row.jp.replace(chr(10), chr(10) + '    ')}\nFR: {row.fr.replace(chr(10), chr(10) + '    ')}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="scene number or database name (menu16, battle16, labels8, names8)")
    ap.add_argument("ids", nargs="*", help="ids or ranges: 94, 94-99, 0xFB90-0xFB9E")
    ap.add_argument("-g", "--grep", help="only entries whose Japanese or French matches this regex")
    args = ap.parse_args()
    name = source(args.source)
    for row in select(pairs(name), parse_ids(args.ids), args.grep):
        print(render(row, hexadecimal=not args.source.isdigit()))


if __name__ == "__main__":
    main()
