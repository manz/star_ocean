"""The story graph, read from the scene scripts alone (notes/text/map_table.md).

A scene's setup branches on the map id (`sys.w[0xc]`) and story state, then places the map's triggers, NPCs and
chests; the entries they fire change maps, set flags and story variables, start battles, open shops. The walk runs
every path of the setup with the set of maps it can be on (the scene's, from the map table): `if sys.w[0xc] == N`
narrows it, any other condition becomes a guard on both sides. Each placed trigger's entry is then walked the same
way for its effects.

    uv run python -m tools.story_graph [MAP ...]      # every map's exits and what its entries do
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import cache

from tools.dialog import SCENES
from tools.map_table import scene_maps
from tools.scene_script import Condition, Instruction, Jump, Value, header, instruction, scene_data
from tools.scene_walk import walk

MAP_ID = ("sys", 0xC)
MAX_CALLS = 32  # nested calls a path may hold: a script calling itself stays finite
PLACEMENTS = {"trigger_tile", "trigger_zone", "npc_create", "chest_create", "actor_create"}
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


def arg(value: object) -> Arg:
    if isinstance(value, Value):
        return value.n if value.table in ("imm", "byte") else str(value)
    return str(value)


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
                found.add(Op(self.scene, point.maps, ins.name, tuple(arg(a) for a in ins.args), guards))
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
    effects: dict[tuple[int, int], frozenset[Op]]  # by entry (kind, id), walked on the maps its placements cover

    def exits(self) -> set[Exit]:
        return set(self._exits())

    def _exits(self) -> Iterator[Exit]:
        for p in self.placements:
            if p.name not in ("trigger_tile", "trigger_zone"):
                continue
            box = (p.args[0], p.args[1], p.args[0], p.args[1]) if p.name == "trigger_tile" else p.args[:4]
            entry = p.args[-1]
            for e in self.effects.get((STEP, entry), frozenset()) if isinstance(entry, int) else ():
                if e.name in ("map_change", "map_change_continue") and e.maps & p.maps:
                    to, kind, x, y = e.args[:4]
                    facing = e.args[4] if e.name == "map_change" else None
                    yield Exit(
                        self.scene,
                        e.maps & p.maps,
                        (box[0], box[1], box[2], box[3]),
                        to,
                        kind,
                        x,
                        y,
                        facing,
                        p.guards | e.guards,
                    )


def _entries(placements: frozenset[Op]) -> dict[tuple[int, int], frozenset[int]]:
    """The entries the placements fire, with the maps each is placed on."""
    out: dict[tuple[int, int], frozenset[int]] = {}
    for p in placements:
        key = None
        if p.name in ("trigger_tile", "trigger_zone") and isinstance(p.args[-1], int):
            key = (STEP, p.args[-1])
        elif p.name in ("npc_create", "actor_create") and isinstance(p.args[0], int):
            key = (TALK, p.args[0])
        if key is not None:
            out[key] = out.get(key, frozenset()) | p.maps
    return out


@cache
def scene_graph(scene: int) -> SceneGraph:
    data = scene_data(scene)
    head = header(data)
    maps = scene_maps().get(scene, frozenset()) | _tested_maps(scene, data)
    start = head.length + int.from_bytes(data[2:4], "little")
    placements = frozenset(_Walker(scene, data, PLACEMENTS).run(start, maps))
    addresses = {(e.kind, e.id): head.length + e.address for e in head.entries}
    effects = {}
    for key, on in _entries(placements).items():
        if key in addresses:
            effects[key] = frozenset(_Walker(scene, data, EFFECTS).run(addresses[key], on))
    return SceneGraph(scene, placements, effects)


def _tested_maps(scene: int, data: bytes) -> frozenset[int]:
    """Maps the scene's code tests for: a test can name a map of another scene (548 in scene 83)."""
    conditions = (i.args[2] for i in walk(data).code.values() if i.name == "if")
    tests = (map_test(c) for c in conditions if isinstance(c, Condition))
    return frozenset(m for m in tests if m is not None)


def graphs() -> list[SceneGraph]:
    return [scene_graph(s) for s in range(1, SCENES + 1)]


def main(argv: list[str] | None = None, echo: Callable[[str], None] = print) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("maps", type=int, nargs="*")
    args = parser.parse_args(argv)
    for g in graphs():
        for e in sorted(g.exits(), key=lambda e: (sorted(e.maps), str(e.box), str(e.to))):
            if args.maps and not e.maps & set(args.maps):
                continue
            guards = " && ".join(sorted(map(str, e.guards)))
            echo(f"scene {g.scene:2} maps {sorted(e.maps)} {e.box} -> {e.to} ({e.x}, {e.y}) {guards}".rstrip())


if __name__ == "__main__":
    main()
