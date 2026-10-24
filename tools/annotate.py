"""Annotate the scene messages (text/fr and text/jp) with how the event scripts use them, as attributes on each
`<sn:pointer>`:

- choice: the menu a `choose` shows (the last `say` before it): its option count, `yes-no` for a count of 0, or
  `dynamic` when the count is a variable or differs between sites. The layout holds a counted menu to one line
  per option (tools/encode_text.py).
- window: the `say` ops that open it: `speaker` (op 0D, window by speaker) or the mode of `say_modeN`.
- trigger: the header entries whose scripts reach it: `start`, `talk N` (A facing actor N), `search` (A with no one
  in front), `touch` (an actor touching the hero), `tile N` (the hero on a trigger tile or zone), `actor N` (an
  actor on an actor trigger) (notes/text/scene_triggers.md).
- unused="1": no reached `say` names it.

Scripts are read with tools.scene_events edits applied, as the patch ships them.

    uv run python -m tools.annotate [--check]
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tools.dialog import SCENES
from tools.rom import ROOT
from tools.scene_script import Instruction, Value, header, scene_data
from tools.scene_walk import roots, walk

TEXTS = [ROOT / "text" / "fr", ROOT / "text" / "jp"]
WINDOWS = {"say": "speaker", "say_mode0": "0", "say_mode1": "1", "say_mode8": "8", "say_mode9": "9"}
SEARCH, TOUCH = 0x7F, 0x7D  # kind 2 entries fired by A with no one in front, and by an actor touching the hero
POINTER = re.compile(r'<sn:pointer id="(\d+)"[^>]*>')


@dataclass
class Usage:
    choices: set[int | str] = field(default_factory=set)
    windows: set[str] = field(default_factory=set)
    triggers: set[str] = field(default_factory=set)

    def attributes(self) -> dict[str, str]:
        if not self.windows:
            return {"unused": "1"}
        out = {}
        if self.choices:
            out["choice"] = choice(self.choices)
        out["window"] = " ".join(sorted(self.windows))
        out["trigger"] = " ".join(sorted(self.triggers, key=_trigger_order))
        return out


def choice(counts: set[int | str]) -> str:
    if len(counts) > 1 or "var" in counts:
        return "dynamic"
    (count,) = counts
    return "yes-no" if count == 0 else str(count)


def _trigger_order(name: str) -> tuple[str, int]:
    kind, _, n = name.partition(" ")
    return kind, int(n) if n else -1


def trigger_name(kind: int, id_: int) -> str:
    if kind == 0:
        return f"talk {id_}"
    if kind == 1:
        return f"actor {id_}"
    return {SEARCH: "search", TOUCH: "touch"}.get(id_, f"tile {id_}")


def menu_counts(code: dict[int, Instruction]) -> dict[int, set[int | str]]:
    """Message -> the option counts of the `choose`s showing it: the last `say` before each, in code order, with no
    `end` or `ret` between."""
    out: dict[int, set[int | str]] = defaultdict(set)
    said = None
    for _, ins in sorted(code.items()):
        if ins.message is not None:
            said = ins.message
        elif ins.name in ("end", "ret"):
            said = None
        elif ins.name == "choose" and said is not None:
            count = ins.args[1]
            assert isinstance(count, Value)
            out[said].add(count.n if count.table in ("imm", "byte") else "var")
    return out


def scene_usage(data: bytes) -> dict[int, Usage]:
    head = header(data)
    starts = [("start", roots(data)[0])] + [(trigger_name(e.kind, e.id), head.length + e.address) for e in head.entries]
    usage: dict[int, Usage] = defaultdict(Usage)
    for name, start in starts:
        for ins in walk(data, [start]).code.values():
            if ins.message is not None:
                usage[ins.message].windows.add(WINDOWS[ins.name])
                usage[ins.message].triggers.add(name)
    for message, counts in menu_counts(walk(data).code).items():
        usage[message].choices |= counts
    return usage


def annotated(text: str, usage: dict[int, Usage]) -> str:
    def tag(m: re.Match[str]) -> str:
        attrs = usage.get(int(m[1]), Usage()).attributes()
        return f'<sn:pointer id="{m[1]}"' + "".join(f' {k}="{v}"' for k, v in attrs.items()) + ">"

    return POINTER.sub(tag, text)


def annotate(write: bool = True, dirs: list[Path] = TEXTS) -> list[Path]:
    """The scene files whose annotations are out of date, rewritten when `write`."""
    out = []
    for scene in range(1, SCENES + 1):
        usage = scene_usage(scene_data(scene, with_edits=True))
        for path in (d / f"scene_{scene:02d}.xml" for d in dirs):
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            new = annotated(text, usage)
            if new == text:
                continue
            out.append(path)
            if write:
                path.write_text(new, encoding="utf-8")
    return out


def main(argv: list[str] | None = None, echo: Callable[[str], None] = print) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="list stale files, write nothing; exit 1 if any")
    args = parser.parse_args(argv)
    changed = annotate(write=not args.check)
    for path in changed:
        echo(f"{'stale' if args.check else 'annotated'} {path.relative_to(ROOT)}")
    if args.check and changed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
