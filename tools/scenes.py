"""Write `text/scenes.xml`: where the scene scripts say each message, for `katsuji preview` (katsuji's
`script_game` reads it), from the annotations `tools.annotate` writes on each pointer (notes/text/annotations.md).

A scene file is a scene, titled by its place banner: the first message its start opens with `[center]` ("Ville de
Clatos"), as `place="scene_05:0"`. Its messages go under what fires them (`trigger`): the start, each NPC talked
to (`talk N`, named by its `npc`), the tiles stepped on, a search, a touch, an actor; in file order. A message no
script reaches (`unused`) is left out.

    uv run python -m tools.scenes   # rewrite text/scenes.xml
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import quoteattr

from katsuji.script import sn

from tools.rom import ROOT

TEXT = ROOT / "text"
SCENES = TEXT / "scenes.xml"
HEAD = '<?xml version="1.0" encoding="utf-8"?>\n<sn:scenes xmlns:sn="http://snes.ninja/ScriptNS">\n'
END = "</sn:scenes>\n"
BANNER = re.compile(r"^(?:\[[^\]]*\])*?\[center\]")
FIRES = re.compile(r"(start|search|touch)|(talk|tile|actor) (\d+)")
ORDER = {"start": 0, "talk": 1, "actor": 2, "tile": 3, "search": 4, "touch": 5}


def document(scenes: list[Path]) -> str:
    """`scenes.xml`: each scene file's messages by trigger, in scene order."""
    return HEAD + "".join(scene(path) for path in scenes) + END


def scene(path: Path) -> str:
    messages = [message for message in sn.read(path) if message.attributes.get("unused") != "1"]
    groups: dict[str, list[sn.Message]] = {}
    for message in messages:
        if trigger := message.attributes.get("trigger"):
            groups.setdefault(trigger, []).append(message)
    banner = next((m for m in messages if m.attributes.get("trigger") == "start" and BANNER.match(m.text)), None)
    title = f"scene {path.stem.removeprefix('scene_')}"
    head = f"  <sn:scene title={quoteattr(title)}" + (f' place="{path.stem}:{banner.id}"' if banner else "") + ">\n"
    inner = "".join(_group(path.stem, trigger, said) for trigger, said in sorted(groups.items(), key=_order))
    return head + inner + "  </sn:scene>\n"


def title(trigger: str, said: list[sn.Message]) -> str:
    """A trigger as it reads: "talk 20 · Puffy", "tiles 1-7", "search"."""
    fired = FIRES.findall(trigger)
    kinds = {word or kind for word, kind, _ in fired}
    numbers = [int(number) for _, _, number in fired if number]
    if len(kinds) != 1 or len(numbers) < 2:
        named = trigger
    else:
        named = f"{kinds.pop()}s {_ranges(numbers)}"
    npcs = Counter(m.attributes["npc"] for m in said if "npc" in m.attributes)
    return f"{named} · {npcs.most_common(1)[0][0]}" if npcs else named


def _group(file: str, trigger: str, said: list[sn.Message]) -> str:
    says = "".join(f'<sn:say ref="{file}:{message.id}"/>' for message in said)
    return f"    <sn:scene title={quoteattr(title(trigger, said))}>{says}</sn:scene>\n"


def _order(item: tuple[str, list[sn.Message]]) -> tuple[int, int, str]:
    """Start first, then the NPCs by number, the actors, the tiles, a search, a touch."""
    fired = FIRES.findall(item[0])
    word, kind, number = fired[0] if fired else ("", "", "")
    return ORDER.get(word or kind, len(ORDER)), int(number or 0), item[0]


def _ranges(numbers: list[int]) -> str:
    """1 2 3 5 → "1-3, 5"."""
    runs: list[list[int]] = []
    for number in sorted(set(numbers)):
        if runs and number == runs[-1][-1] + 1:
            runs[-1].append(number)
        else:
            runs.append([number])
    return ", ".join(f"{run[0]}-{run[-1]}" if len(run) > 1 else str(run[0]) for run in runs)


def main() -> None:
    SCENES.write_text(document(sorted((TEXT / "fr").glob("scene_*.xml"))), encoding="utf-8")


if __name__ == "__main__":
    main()
