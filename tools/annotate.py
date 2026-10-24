"""Annotate the scene messages (text/fr and text/jp) with how the event scripts use them, as attributes on each
`<sn:pointer>`:

- choice: the menu a `choose` shows (the last `say` before it): its option count, `yes-no` for a count of 0, or
  `dynamic` when the count is a variable or differs between sites. The layout holds a counted menu to one line
  per option (tools/encode_text.py).
- window: the `say` ops that open it: `speaker` (op 0D, window by speaker) or the mode of `say_modeN`.
- trigger: the header entries whose scripts reach it: `start`, `talk N` (A facing actor N), `search` (A with no one
  in front), `touch` (an actor touching the hero), `tile N` (the hero on a trigger tile or zone), `actor N` (an
  actor on an actor trigger) (notes/text/scene_triggers.md).
- npc: who the hero talks to for the `talk N` entries reaching it, named from the speaker labels of the messages
  that actor's script says, in the file's own language (`Ben le Marin`, `船乗りベン`); party members (`[nick:...]`)
  and `???` never name an actor, so one that is a party member stays unnamed. Several are joined by `; `.
- unused="1": no reached `say` names it.

Scripts are read with tools.scene_events edits applied, as the patch ships them.

    uv run python -m tools.annotate [--check]
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
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
PREFIX, NAMESPACE = "sn", "http://snes.ninja/ScriptNS"
ET.register_namespace(PREFIX, NAMESPACE)
OPTION = re.compile(r"^(?:\[[^\]]*\])*\d\. ")
PARTY = re.compile(r"\[(?:nick|name):")
TAG = re.compile(r"\[[^\]]*\]")
LABEL_CHARS = 40  # a French speaker label is one short line; longer [br] lines are speech


@dataclass
class Usage:
    choices: set[int | str] = field(default_factory=set)
    windows: set[str] = field(default_factory=set)
    triggers: set[str] = field(default_factory=set)
    talks: set[int] = field(default_factory=set)  # actors whose talk entry reaches it

    def attributes(self, npcs: dict[int, str]) -> dict[str, str]:
        if not self.windows:
            return {"unused": "1"}
        out = {}
        if self.choices:
            out["choice"] = choice(self.choices)
        out["window"] = " ".join(sorted(self.windows))
        out["trigger"] = " ".join(sorted(self.triggers, key=_trigger_order))
        names = sorted({npcs[n] for n in self.talks if n in npcs})
        if names:
            out["npc"] = "; ".join(names)
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
                if name.startswith("talk "):
                    usage[ins.message].talks.add(int(name[5:]))
    for message, counts in menu_counts(walk(data).code).items():
        usage[message].choices |= counts
    return usage


def labels(text: str, japanese: bool) -> list[str]:
    """The speaker labels opening the message's pages, party members and `???` left out. French: a short first line
    ending in [br]; Japanese: the name before 「."""
    out = []
    for page in text.split("[page]"):
        first = page.lstrip("\n").split("\n")[0]
        if japanese:
            label = first.partition("「")[0] if "「" in first else ""
        elif first.endswith("[br]") and not OPTION.match(first) and not first.startswith("[center]"):
            label = first.removesuffix("[br]")
        else:
            label = ""
        if PARTY.search(label):
            continue
        name = TAG.sub("", label).strip()
        if name.strip("?？") and len(name) <= LABEL_CHARS:
            out.append(name)
    return out


def npc_names(texts: dict[int, str], usage: dict[int, Usage], japanese: bool) -> dict[int, str]:
    """Actor -> its most frequent speaker label over the messages its talk entry reaches."""
    counts: dict[int, Counter[str]] = defaultdict(Counter)
    for message, use in usage.items():
        for actor in use.talks:
            counts[actor].update(labels(texts.get(message, ""), japanese))
    return {actor: c.most_common(1)[0][0] for actor, c in counts.items() if c}


def annotated(text: str, usage: dict[int, Usage], japanese: bool = False) -> str:
    """The scene file with each pointer's attributes replaced by `id` plus its usage's; the prolog stays as written
    (ElementTree writes its own)."""
    root = ET.fromstring(text.encode("utf-8"))
    npcs = npc_names({int(node.attrib["id"]): node.text or "" for node in root}, usage, japanese)
    for node in root:
        message = node.attrib["id"]
        node.attrib.clear()
        node.attrib.update({"id": message, **usage.get(int(message), Usage()).attributes(npcs)})
    end = f"</{PREFIX}:script>"
    head, tail = text[: text.index(f"<{PREFIX}:script")], text[text.rindex(end) + len(end) :]
    return head + ET.tostring(root, encoding="unicode") + tail


def annotate(write: bool = True, dirs: list[Path] = TEXTS) -> list[Path]:
    """The scene files whose annotations are out of date, rewritten when `write`."""
    out = []
    for scene in range(1, SCENES + 1):
        usage = scene_usage(scene_data(scene, with_edits=True))
        for path in (d / f"scene_{scene:02d}.xml" for d in dirs):
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            new = annotated(text, usage, japanese=path.parent.name == "jp")
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
