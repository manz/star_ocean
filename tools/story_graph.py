"""The story graph, read from the scene scripts alone (notes/text/map_table.md).

A scene's setup branches on the map id (`sys.w[0xc]`) and story state, then places the map's triggers, NPCs and
chests; the entries they fire change maps, set flags and story variables, start battles, open shops. The walk runs
every path of the setup with the set of maps it can be on (the scene's, from the map table): `if sys.w[0xc] == N`
narrows it, any other condition becomes a guard on both sides. Each placed trigger's entry is then walked the same
way for its effects.

The story counter `var.w[0x10]` only goes up over the game; `steps` are its writes, each pinned to the value(s) its
guards allow: what the drive does next from a save's value.

    uv run python -m tools.story_graph [MAP ...]      # every map's exits
    uv run python -m tools.story_graph --story [V ...] # the counter's steps (from value V)
    uv run python -m tools.story_graph --json build/story_graph.json  # all of it for the drive
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from tools.dialog import SCENES
from tools.map_table import map_scenes, scene_maps
from tools.scene_script import (
    STORES,
    Condition,
    Expression,
    Instruction,
    Jump,
    Term,
    Value,
    header,
    instruction,
    scene_data,
)
from tools.scene_walk import walk

MAP_ID = ("sys", 0xC)
DEBUG_SCENE = 1  # map 0's start menu: sets the counter to any chapter's value, not a story step
MAX_CALLS = 32  # nested calls a path may hold: a script calling itself stays finite
PLACEMENTS = {"trigger_tile", "trigger_zone", "npc_create", "chest_create", "actor_create"}
STORY = "var.w[0x10]"  # the story counter: only goes up over the game (12 at the start, 173 at the Seven Star Ruins)
EFFECTS = {
    "map_change",
    "map_change_continue",
    "flag_on",
    "flag_off",
    "set",
    "battle_start",
    "open_shop",
    "item_add",
    "party_join",
    "party_leave",
    "inc",
    "dec",
}
TALK, STEP = 0, 2  # entry kinds: A facing actor n / stepping on a trigger


@dataclass(frozen=True)
class Guard:
    """A condition the path took (holds) or went around (not holds)."""

    condition: Condition
    holds: bool

    def __str__(self) -> str:
        return str(self.condition) if self.holds else f"!({self.condition})"


Arg = int | str  # a number, or a variable's name (var.w[0x10])


@dataclass(frozen=True)
class Op:
    """One placement or effect: the instruction, the maps it can run on and the guards on its path."""

    scene: int
    maps: frozenset[int]
    name: str
    args: tuple[Arg, ...]
    guards: frozenset[Guard]  # what must hold: the conditions every path to it took


@dataclass(frozen=True)
class Exit:
    scene: int
    maps: frozenset[int]  # the maps the trigger is placed on
    box: tuple[Arg, Arg, Arg, Arg]  # x1, y1, x2, y2 in 16 px cells (a tile: x, y, x, y)
    to: Arg  # the map
    kind: Arg  # 0 fade, 1 none, 2 door
    x: Arg
    y: Arg
    facing: Arg | None  # map_change_continue has none
    guards: frozenset[Guard]  # the trigger's and the entry's


@dataclass(frozen=True)
class Trigger:
    kind: str  # arrive (the setup itself), step (a trigger tile / zone), talk (A facing an actor)
    box: tuple[Arg, Arg, Arg, Arg] | None = None
    actor: int | None = None


ARRIVE = Trigger("arrive")


@dataclass(frozen=True)
class Action:
    """An effect and what fires it, on the maps both cover, with the guards of both."""

    scene: int
    maps: frozenset[int]
    trigger: Trigger
    name: str
    args: tuple[Arg, ...]
    guards: frozenset[Guard]


@dataclass(frozen=True)
class Step:
    """One move of the story counter."""

    scene: int
    maps: frozenset[int]
    at: int | None  # the value it needs (None: no guard pins one)
    to: Arg | None  # the value it writes (None: an `inc` from an unpinned value)
    trigger: Trigger
    guards: frozenset[Guard]


def arg(value: object) -> Arg:
    if isinstance(value, Value):
        return value.n if value.table in ("imm", "byte") else str(value)
    if isinstance(value, Expression):
        if len(value.tokens) == 1:
            return arg(value.tokens[0])
        return " ".join(map(str, value.tokens))
    return str(value)


def _args(ins: Instruction) -> tuple[Arg, ...]:
    """The operands; a `set` as (variable, store, value): `=`, `+=`, ... (scene_script.STORES)."""
    if ins.name == "set":
        dest, value = ins.args
        assert isinstance(dest, Value)
        return arg(dest), STORES[(dest.flags >> 3) & 7], arg(value)
    return tuple(arg(a) for a in ins.args)


def map_test(condition: Condition) -> int | None:
    """N when the condition is exactly `sys.w[0xc] == N`."""
    if len(condition.terms) != 1 or condition.terms[0].compare != 0:
        return None
    a, b = condition.terms[0].values
    return b.n if (a.table, a.n) == MAP_ID and b.table in ("imm", "byte") else None


def _target(operand: object) -> int:
    assert isinstance(operand, Jump) and isinstance(operand.target, int)
    return operand.target


@dataclass(frozen=True)
class _Point:
    """Where a path is: the code, the maps it can be on, the calls to return from."""

    pos: int
    maps: frozenset[int]
    returns: tuple[int, ...]


class _Walker:
    """Every path from one root, as a data flow: each point keeps the guards common to every path reaching it (the
    conditions that must hold there), narrowed until nothing changes. `keep` picks the instructions recorded."""

    def __init__(self, scene: int, data: bytes, keep: set[str]) -> None:
        self.scene, self.data, self.keep = scene, data, keep
        self.base = header(data).length
        self.guards: dict[_Point, frozenset[Guard]] = {}

    def run(self, pos: int, maps: frozenset[int]) -> set[Op]:
        todo = [(_Point(pos, maps, ()), frozenset[Guard]())]
        while todo:
            point, guards = todo.pop()
            if point.pos >= len(self.data) or len(point.returns) > MAX_CALLS:
                continue
            old = self.guards.get(point)
            if old is not None:
                if old <= guards:
                    continue
                guards = old & guards
            self.guards[point] = guards
            todo += self._step(point, guards)
        return self._found()

    def _found(self) -> set[Op]:
        found = set()
        for point, guards in self.guards.items():
            ins = instruction(self.data, point.pos, self.base)
            if ins.name in self.keep:
                found.add(Op(self.scene, point.maps, ins.name, _args(ins), guards))
        return found

    def _step(self, p: _Point, guards: frozenset[Guard]) -> list[tuple[_Point, frozenset[Guard]]]:
        ins = instruction(self.data, p.pos, self.base)
        nxt = p.pos + ins.size
        match ins.name:
            case "if":
                return self._branch(p, guards, ins)
            case "goto":
                return [(_Point(_target(ins.args[0]), p.maps, p.returns), guards)]
            case "call":
                return [(_Point(_target(ins.args[0]), p.maps, (*p.returns, nxt)), guards)]
            case "ret":
                return [(_Point(p.returns[-1], p.maps, p.returns[:-1]), guards)] if p.returns else []
            case "end":
                return []
        return [(_Point(nxt, p.maps, p.returns), guards)]

    def _branch(self, p: _Point, guards: frozenset[Guard], ins: Instruction) -> list[tuple[_Point, frozenset[Guard]]]:
        then, other, condition = _target(ins.args[0]), _target(ins.args[1]), ins.args[2]
        assert isinstance(condition, Condition)
        m = map_test(condition)
        if m is None:
            return [
                (_Point(then, p.maps, p.returns), guards | {Guard(condition, True)}),
                (_Point(other, p.maps, p.returns), guards | {Guard(condition, False)}),
            ]
        out = [(_Point(other, p.maps - {m}, p.returns), guards)] if p.maps - {m} else []
        if m in p.maps:
            out.append((_Point(then, frozenset({m}), p.returns), guards))
        return out


@dataclass(frozen=True)
class SceneGraph:
    scene: int
    placements: frozenset[Op]
    arrivals: frozenset[Op]  # effects the setup runs itself, on arrival
    effects: dict[tuple[int, int], frozenset[Op]]  # by entry (kind, id), walked on the maps its placements cover

    def actions(self) -> set[Action]:
        out = {Action(self.scene, a.maps, ARRIVE, a.name, a.args, a.guards) for a in self.arrivals}
        for p in self.placements:
            trigger, entry = _trigger(p)
            if trigger is None:
                continue
            for e in self.effects.get(entry, frozenset()):
                if e.maps & p.maps:
                    out.add(Action(self.scene, e.maps & p.maps, trigger, e.name, e.args, p.guards | e.guards))
        return out

    def exits(self) -> set[Exit]:
        """Map changes fired by stepping on a trigger."""
        out = set()
        for a in self.actions():
            if a.name in ("map_change", "map_change_continue") and a.trigger.box is not None:
                to, kind, x, y = a.args[:4]
                facing = a.args[4] if a.name == "map_change" else None
                out.add(Exit(self.scene, a.maps, a.trigger.box, to, kind, x, y, facing, a.guards))
        return out

    def steps(self) -> set[Step]:
        """Writes to the story counter, one per value the guards pin (`var.w[0x10] == v`, or a list of them)."""
        out = set()
        for a in self.actions():
            if not a.args or a.args[0] != STORY or a.name not in ("inc", "set") or not _allowed(a.guards):
                continue
            ats: list[int | None] = [*sorted(_pinned(a.guards))] or [None]
            for at in ats:
                to = _written(a, at)
                out.add(Step(self.scene, a.maps, at, to, a.trigger, a.guards))
        return out


def _written(a: Action, at: int | None) -> Arg | None:
    """The counter after the action, from `at` (None when it depends on an unknown value)."""
    if a.name == "inc":
        return at + 1 if at is not None else None
    _, store, value = a.args
    if store == "=":
        return value
    if store == "+=" and isinstance(value, int) and at is not None:
        return at + value
    return None


def _trigger(p: Op) -> tuple[Trigger | None, tuple[int, int]]:
    """What fires a placement's entry, and the entry."""
    if p.name in ("trigger_tile", "trigger_zone") and isinstance(p.args[-1], int):
        box = (p.args[0], p.args[1], p.args[0], p.args[1]) if p.name == "trigger_tile" else p.args[:4]
        return Trigger("step", box=(box[0], box[1], box[2], box[3])), (STEP, p.args[-1])
    if p.name in ("npc_create", "actor_create") and isinstance(p.args[0], int):
        return Trigger("talk", actor=p.args[0]), (TALK, p.args[0])
    return None, (0, 0)


COUNTER = frozenset(range(0x100))  # the values the story counter takes (the debug start sets up to 200)
PINNED = 8  # at most this many values left: the step is pinned to each of them


def _allowed(guards: frozenset[Guard]) -> frozenset[int]:
    """The counter values every guard allows. Empty: the guards contradict (a placement of an actor paired with the
    entry path of another placement), the action never happens."""
    allowed = COUNTER
    for g in guards:
        values = _story_values(g.condition)
        if values is not None:
            allowed &= values if g.holds else COUNTER - values
    return allowed


def _pinned(guards: frozenset[Guard]) -> frozenset[int]:
    """The counter values allowed, when few enough to name (`var.w[0x10] == v`, a list of them, a short range)."""
    allowed = _allowed(guards)
    return allowed if len(allowed) <= PINNED else frozenset()


def _story_values(c: Condition) -> frozenset[int] | None:
    """The counter values that make the condition true, when it reads nothing but the counter (an `&&` may also
    test other things: the counter part still bounds it). None: the condition says nothing about the counter."""
    tests = [_story_test(t) for t in c.terms]
    if all(j == 0 for j in c.joiners):  # ||
        known = [v for v in tests if v is not None]
        return frozenset().union(*known) if len(known) == len(tests) else None
    if all(j == 1 for j in c.joiners):  # &&
        known = [v for v in tests if v is not None]
        return COUNTER.intersection(*known) if known else None
    return None


COMPARE_TEST: dict[int, Callable[[int, int], bool]] = {
    0: lambda v, n: v == n,
    1: lambda v, n: v > n,
    2: lambda v, n: v < n,
    3: lambda v, n: v != n,
    4: lambda v, n: v >= n,
    5: lambda v, n: v <= n,
}


def _story_test(t: Term) -> frozenset[int] | None:
    if t.compare not in COMPARE_TEST or len(t.values) != 2:
        return None
    a, b = t.values
    if str(a) != STORY or b.table not in ("imm", "byte"):
        return None
    test = COMPARE_TEST[t.compare]
    return frozenset(v for v in COUNTER if test(v, b.n))


def _entries(placements: frozenset[Op]) -> dict[tuple[int, int], frozenset[int]]:
    """The entries the placements fire, with the maps each is placed on."""
    out: dict[tuple[int, int], frozenset[int]] = {}
    for p in placements:
        trigger, key = _trigger(p)
        if trigger is not None:
            out[key] = out.get(key, frozenset()) | p.maps
    return out


@cache
def scene_graph(scene: int) -> SceneGraph:
    data = scene_data(scene)
    head = header(data)
    maps = scene_maps().get(scene, frozenset()) | _tested_maps(scene, data)
    start = head.length + int.from_bytes(data[2:4], "little")
    setup = _Walker(scene, data, PLACEMENTS | EFFECTS).run(start, maps)
    placements = frozenset(op for op in setup if op.name in PLACEMENTS)
    arrivals = frozenset(op for op in setup if op.name in EFFECTS)
    addresses = {(e.kind, e.id): head.length + e.address for e in head.entries}
    effects = {}
    for key, on in _entries(placements).items():
        if key in addresses:
            effects[key] = frozenset(_Walker(scene, data, EFFECTS).run(addresses[key], on))
    return SceneGraph(scene, placements, arrivals, effects)


def _tested_maps(scene: int, data: bytes) -> frozenset[int]:
    """Maps the scene's code tests for: a test can name a map of another scene (548 in scene 83)."""
    conditions = (i.args[2] for i in walk(data).code.values() if i.name == "if")
    tests = (map_test(c) for c in conditions if isinstance(c, Condition))
    return frozenset(m for m in tests if m is not None)


def graphs() -> list[SceneGraph]:
    return [scene_graph(s) for s in range(1, SCENES + 1)]


def main(argv: list[str] | None = None, echo: Callable[[str], None] = print) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("numbers", type=int, nargs="*", help="maps (or counter values with --story)")
    parser.add_argument("--story", action="store_true", help="the story counter's steps instead of exits")
    parser.add_argument("--json", type=Path, help="write the whole graph here for the drive (betaplayer_so)")
    args = parser.parse_args(argv)
    if args.json:
        args.json.write_text(json.dumps(export(), indent=1))
        echo(f"{args.json}")
        return
    if args.story:
        for line in _story_lines(set(args.numbers)):
            echo(line)
        return
    for g in graphs():
        for e in sorted(g.exits(), key=lambda e: (sorted(e.maps), str(e.box), str(e.to))):
            if args.numbers and not e.maps & set(args.numbers):
                continue
            guards = " && ".join(sorted(map(str, e.guards)))
            echo(f"scene {g.scene:2} maps {sorted(e.maps)} {e.box} -> {e.to} ({e.x}, {e.y}) {guards}".rstrip())


def _counter(guards: frozenset[Guard]) -> list[int] | None:
    """The counter values the guards allow, None for any."""
    allowed = _allowed(guards)
    return None if allowed == COUNTER else sorted(allowed)


def export() -> dict[str, object]:
    """The graph as plain data: map scenes, exits and story steps, each with the counter values it needs (`counter`,
    null for any) and its other guards as text. Exit boxes are 16 px cells (inclusive), arrivals 8 px units."""
    gs = graphs()
    exits = [
        {
            "scene": e.scene,
            "maps": sorted(e.maps),
            "box": list(e.box),
            "to": e.to,
            "kind": e.kind,
            "x": e.x,
            "y": e.y,
            "facing": e.facing,
            "counter": _counter(e.guards),
            "guards": sorted(map(str, e.guards)),
        }
        for g in gs
        for e in g.exits()
        if _allowed(e.guards)
    ]
    steps = [
        {
            "scene": s.scene,
            "maps": sorted(s.maps),
            "at": s.at,
            "to": s.to,
            "trigger": {"kind": s.trigger.kind, "box": s.trigger.box and list(s.trigger.box), "actor": s.trigger.actor},
            "guards": sorted(map(str, s.guards)),
        }
        for g in gs
        if g.scene != DEBUG_SCENE
        for s in g.steps()
    ]
    order = lambda d: json.dumps(d, sort_keys=True)
    return {
        "scenes": {str(m): scene for m, scene in sorted(map_scenes().items())},
        "exits": sorted(exits, key=order),
        "steps": sorted(steps, key=order),
    }


def _story_lines(values: set[int]) -> list[str]:
    steps = [s for g in graphs() if g.scene != DEBUG_SCENE for s in g.steps()]
    lines = []
    for s in sorted(steps, key=lambda s: (s.at is None, s.at or 0, s.scene, sorted(s.maps), str(s.trigger))):
        if values and s.at not in values:
            continue
        t = s.trigger
        how = t.kind if t.kind == "arrive" else f"{t.kind} {t.box if t.box is not None else t.actor}"
        lines.append(f"{s.at} -> {s.to}: scene {s.scene} maps {sorted(s.maps)} {how}")
    return lines


if __name__ == "__main__":
    main()
