"""Walk the scene event scripts from where the game enters them: the start-up (right after the header) and every
header entry, following goto / call / if. What the walk never reaches is code no trigger can run. Also checks that
every trigger op names an entry the header has (trigger_* fire kind 2, actor_trigger_* kind 1).

    uv run python -m tools.scene_walk [SCENE ...] [--edited]
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass

from tools.dialog import SCENES
from tools.scene_script import OPS, Instruction, Value, header, instruction, scene_data

STOPS = {"end", "ret", "goto", "if"}  # no fall-through: if goes to its then or else
TRIGGERS = {"trigger_tile": 2, "trigger_zone": 2, "actor_trigger_tile": 1, "actor_trigger_rect": 1}


@dataclass(frozen=True)
class Walk:
    code: dict[int, Instruction]  # every reached instruction by offset
    start: int  # the code area: header end ..
    end: int  # .. data end

    def reached_bytes(self) -> int:
        return sum(i.size for i in self.code.values())

    def unreached(self) -> list[tuple[int, int]]:
        """Offset ranges [start, end) of the code area no reached instruction covers."""
        covered = sorted((o, o + i.size) for o, i in self.code.items())
        gaps, at = [], self.start
        for lo, hi in covered:
            if lo > at:
                gaps.append((at, lo))
            at = max(at, hi)
        if at < self.end:
            gaps.append((at, self.end))
        return gaps


def roots(data: bytes) -> list[int]:
    head = header(data)
    start_up = head.length + int.from_bytes(data[2:4], "little")
    return [start_up] + [head.length + e.address for e in head.entries]


def walk(data: bytes, start: list[int] | None = None) -> Walk:
    """From `start` (default: every root)."""
    head = header(data)
    code: dict[int, Instruction] = {}
    todo = roots(data) if start is None else list(start)
    while todo:
        pos = todo.pop()
        while pos < len(data) and pos not in code:
            ins = instruction(data, pos, head.length)
            code[pos] = ins
            todo += ins.targets
            if ins.name in STOPS:
                break
            pos += ins.size
    return Walk(code, head.length, len(data))


def missing_entries(data: bytes, reached: Walk) -> list[tuple[int, int, int]]:
    """(offset, kind, id) of reached trigger ops whose entry the header lacks (an immediate id only)."""
    have = {(e.kind, e.id) for e in header(data).entries}
    out = []
    for off, ins in sorted(reached.code.items()):
        kind = TRIGGERS.get(ins.name)
        if kind is None:
            continue
        entry = ins.args[-1]
        if isinstance(entry, Value) and entry.table in ("imm", "byte") and (kind, entry.n) not in have:
            out.append((off, kind, entry.n))
    return out


def dead_messages(data: bytes, lo: int, hi: int) -> list[int]:
    """Messages said by the code in [lo, hi), read linearly (a gap starts on an instruction)."""
    base, out, pos = header(data).length, [], lo
    while pos < hi and data[pos] in OPS:
        ins = instruction(data, pos, base)
        if ins.message is not None:
            out.append(ins.message)
        pos += ins.size
    return out


def report(scene: int, data: bytes) -> list[str]:
    w = walk(data)
    total = w.end - w.start
    lines = [f"scene {scene:2d}: {w.reached_bytes()}/{total} bytes reached ({100 * w.reached_bytes() / total:.1f}%)"]
    for lo, hi in w.unreached():
        said = dead_messages(data, lo, hi)
        lines.append(f"  unreached {lo:04x}-{hi - 1:04x} ({hi - lo} bytes)" + (f", messages {said}" if said else ""))
    lines += [
        f"  {off:04x}: trigger names entry {kind}/{id_:#04x}, absent" for off, kind, id_ in missing_entries(data, w)
    ]
    return lines


def main(argv: list[str] | None = None, echo: Callable[[str], None] = print) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenes", type=int, nargs="*")
    parser.add_argument("--edited", action="store_true", help="with tools.scene_events edits applied")
    args = parser.parse_args(argv)
    reached = total = 0
    for scene in args.scenes or range(1, SCENES + 1):
        data = scene_data(scene, args.edited)
        w = walk(data)
        reached, total = reached + w.reached_bytes(), total + w.end - w.start
        for line in report(scene, data):
            echo(line)
    echo(f"all: {reached}/{total} bytes reached ({100 * reached / total:.1f}%)")


if __name__ == "__main__":
    main()
