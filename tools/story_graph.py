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
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from typing import Any

from tools.dialog import SCENES
from tools.map_table import map_scenes, scene_maps
from tools.scene_script import (
    STORES,
    Condition,
    Expression,
    Index,
    Instruction,
    Jump,
    Operator,
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
    "tile_attr_fill",
    "tile_attr_set",
    "actor_field_or",
}
WALL = 0x40  # the collision code of a wall cell
WALL_OPS = ("tile_attr_fill", "tile_attr_set")  # the last operand: the cells' collision code (0: open floor)
TALK, STEP = 0, 2  # entry kinds: A facing actor n / stepping on a trigger
USE = (STEP, 0x7F)  # A with no actor in front: C8:0000 puts the equipped item ($0592) in var.w[0xc] first
ITEM = "var.w[0xc]"


@dataclass(frozen=True)
class Guard:
    """A condition the path took (holds) or went around (not holds). `flag`: the condition tests a story flag, its
    `flag_test` result stored in the system variable it reads (`flag_test 1; store_result sys[8]; if sys.w[0x8] ==
    0`)."""

    condition: Condition
    holds: bool
    flag: int | None = None

    def __str__(self) -> str:
        if self.flag is not None:
            return f"flag[{self.flag}]" if self.flag_on() else f"!flag[{self.flag}]"
        return str(self.condition) if self.holds else f"!({self.condition})"

    def flag_on(self) -> bool | None:
        """The flag's state the guard needs (None: not a flag guard)."""
        if self.flag is None:
            return None
        return self.holds != (self.condition.terms[0].compare == 0)  # holds `== 0` or fails `!= 0`: off


Arg = int | str  # a number, or a variable's name (var.w[0x10])


@dataclass(frozen=True)
class Op:
    """One placement or effect: the instruction, the maps it can run on and the guards on its path."""

    scene: int
    maps: frozenset[int]
    name: str
    args: tuple[Arg, ...]
    guards: frozenset[Guard]  # what must hold: the conditions every path to it took
    zone: tuple[int, int, int, int] | None = None  # the hero's box an `actor_in_box` before it checked (16 px cells)


@dataclass(frozen=True)
class Exit:
    scene: int
    maps: frozenset[int]  # the maps the trigger is placed on
    box: tuple[Arg, Arg, Arg, Arg] | None  # x1, y1, x2, y2 in 16 px cells (a tile: x, y, x, y); None: a talk
    to: Arg  # the map
    kind: Arg  # 0 fade, 1 none, 2 door
    x: Arg
    y: Arg
    facing: Arg | None  # map_change_continue has none
    guards: frozenset[Guard]  # the trigger's and the entry's
    actor: int | None = None  # talking to this actor takes the hero there (the boat to Astral)


@dataclass(frozen=True)
class Trigger:
    kind: str  # arrive (the setup itself), step (a trigger tile / zone), talk (A facing an actor), use (A, an item on)
    box: tuple[Arg, Arg, Arg, Arg] | None = None
    actor: int | None = None
    item: int | None = None  # use: the item to equip


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
    tested: int | None = None  # the flag the last instruction tested
    results: frozenset[tuple[int, int]] = frozenset()  # (system variable, flag) the flag tests stored
    consts: frozenset[tuple[int, int]] = frozenset()  # (variable, value): a flag op's variable set to a number
    zone: tuple[int, int, int, int] | None = None  # the hero's box the last `actor_in_box` checked
    story: frozenset[int] | None = None  # the counter values the path's tests left (None: any). Paths that tested
    # it apart stay apart: map 203's zone is placed at 93 and at 109, a meet would keep neither
    written: frozenset[str] = field(default=frozenset(), compare=False)  # variables the path set: a test on one is
    # the script's own (map 507's `var[0x40]` loop), not something the story needs first

    def at(self, pos: int, maps: frozenset[int] | None = None, returns: tuple[int, ...] | None = None) -> _Point:
        """The path moved on: the test result stays only right after its `flag_test`."""
        return replace(
            self,
            pos=pos,
            maps=self.maps if maps is None else maps,
            returns=self.returns if returns is None else returns,
            tested=None,
        )

    def boxed(self) -> _Point:
        """Past an `actor_in_box` on the hero: the box it checked, when the variables hold numbers."""
        held = dict(self.consts)
        if held.get(0) != 0 or any(n not in held for n in BOX_VARS[1:]):
            return self
        x1, y1, x2, y2 = (held[n] // 2 for n in BOX_VARS[1:])
        return replace(self, zone=(x1, y1, x2, y2))

    def flag(self, operand: object) -> int | None:
        """A flag op's operand as a number: an immediate, or a variable a `set` gave one (map 234's switch: `set
        var.w[0x4f] = 55`, then `flag_on var.w[0x4f]`)."""
        if isinstance(operand, Value) and operand.table == "imm":
            return operand.n
        if isinstance(operand, Value) and operand.table == "var":
            return next((v for n, v in self.consts if n == operand.n), None)
        return None


FLAG_OPS = ("flag_on", "flag_off", "flag_test")


def _const_set(ins: Instruction) -> tuple[int, int | None] | None:
    """`set var[n] = value`: (n, the value when a lone number, else None); None for anything else."""
    if ins.name != "set":
        return None
    dest, value = ins.args
    if not isinstance(dest, Value) or dest.table != "var":
        return None
    number = _number(value) if isinstance(value, Expression) else None
    return dest.n, number if STORES[(dest.flags >> 3) & 7] == "=" else None


RPN: dict[str, Callable[[int, int], int]] = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b}


def _number(e: Expression) -> int | None:
    """An expression of numbers alone (`14 2 *`), worked out; None when it reads anything else."""
    stack: list[int] = []
    for t in e.tokens:
        if isinstance(t, Value) and t.table == "imm":
            stack.append(t.n)
        elif isinstance(t, Operator) and str(t) in RPN and len(stack) >= 2:
            b, a = stack.pop(), stack.pop()
            stack.append(RPN[str(t)](a, b))
        else:
            return None
    return stack[0] if len(stack) == 1 else None


ACTOR_IN_BOX = 22  # syscall: is actor var.w[0x0] in the 8 px box var.w[0x2], [0x4] to [0x6], [0x8]
BOX_VARS = (0, 2, 4, 6, 8)


def _is_box_test(ins: Instruction) -> bool:
    a = ins.args[0] if ins.args else None
    return ins.name == "syscall" and isinstance(a, Value) and a.n == ACTOR_IN_BOX


class _Walker:
    """Every path from one root, as a data flow: each point keeps the guards common to every path reaching it (the
    conditions that must hold there), narrowed until nothing changes. `keep` picks the instructions recorded."""

    def __init__(self, scene: int, data: bytes, keep: set[str]) -> None:
        self.scene, self.data, self.keep = scene, data, keep
        self.base = header(data).length
        self.guards: dict[_Point, frozenset[Guard]] = {}
        self.tracked: frozenset[int] = frozenset()  # the variables flag ops read their flag from

    def run(self, pos: int, maps: frozenset[int]) -> set[Op]:
        self._flow(pos, maps)
        tracked = frozenset(
            a.n
            for point in self.guards
            for ins in [instruction(self.data, point.pos, self.base)]
            if ins.name in FLAG_OPS
            for a in ins.args
            if isinstance(a, Value) and a.table == "var"
        )
        if any(_is_box_test(instruction(self.data, point.pos, self.base)) for point in self.guards):
            tracked |= frozenset(BOX_VARS)
        if tracked:  # again, keeping what those variables hold
            self.guards, self.tracked = {}, tracked
            self._flow(pos, maps)
        return self._found()

    def _flow(self, pos: int, maps: frozenset[int]) -> None:
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

    def _found(self) -> set[Op]:
        found = set()
        for point, guards in self.guards.items():
            ins = instruction(self.data, point.pos, self.base)
            if ins.name in self.keep:
                args = _args(ins)
                if ins.name in FLAG_OPS and (n := point.flag(ins.args[0])) is not None:
                    args = (n,)
                found.add(Op(self.scene, point.maps, ins.name, args, guards, point.zone))
        return found

    def _step(self, p: _Point, guards: frozenset[Guard]) -> list[tuple[_Point, frozenset[Guard]]]:
        ins = instruction(self.data, p.pos, self.base)
        nxt = p.pos + ins.size
        match ins.name:
            case "if":
                return self._branch(p, guards, ins)
            case "goto":
                return [(p.at(_target(ins.args[0])), guards)]
            case "call":
                return [(p.at(_target(ins.args[0]), returns=(*p.returns, nxt)), guards)]
            case "ret":
                return [(p.at(p.returns[-1], returns=p.returns[:-1]), guards)] if p.returns else []
            case "end":
                return []
            case "flag_test" if (flag := p.flag(ins.args[0])) is not None:
                return [(replace(p, pos=nxt, tested=flag), guards)]
            case "syscall" if _is_box_test(ins):
                return [(p.at(nxt).boxed(), guards)]
        return [(_wrote(_counted(self._keep_const(_with_result(p.at(nxt), ins, p.tested), ins), ins), ins), guards)]

    def _keep_const(self, p: _Point, ins: Instruction) -> _Point:
        if (c := _const_set(ins)) is None or c[0] not in self.tracked:
            return p
        n, value = c
        consts = frozenset(k for k in p.consts if k[0] != n) | ({(n, value)} if value is not None else set())
        return replace(p, consts=consts)

    def _test(
        self, p: _Point, guards: frozenset[Guard], condition: Condition, then: int, other: int
    ) -> list[tuple[_Point, frozenset[Guard]]]:
        """Both ways past a test, each with its guard; a test on the counter narrows the values each way keeps and
        drops a way none are left on. Failing an `&&` says nothing of its counter part."""
        flag = _flag_test(condition, p.results)
        if _reads(condition) & p.written:
            return [(p.at(then), guards), (p.at(other), guards)]
        values = _story_values(condition)
        if values is None:
            return [
                (p.at(to), guards | {Guard(condition, holds, flag)}) for to, holds in ((then, True), (other, False))
            ]
        was = COUNTER if p.story is None else p.story
        both = any(j == 1 for j in condition.joiners)
        sides = ((then, True, was & values), (other, False, was if both else was - values))
        return [
            (replace(p.at(to), story=story), guards | {Guard(condition, holds, flag)})
            for to, holds, story in sides
            if story
        ]

    def _branch(self, p: _Point, guards: frozenset[Guard], ins: Instruction) -> list[tuple[_Point, frozenset[Guard]]]:
        then, other, condition = _target(ins.args[0]), _target(ins.args[1]), ins.args[2]
        assert isinstance(condition, Condition)
        m = map_test(condition)
        if m is None:
            return self._test(p, guards, condition, then, other)
        out = [(p.at(other, maps=p.maps - {m}), guards)] if p.maps - {m} else []
        if m in p.maps:
            out.append((p.at(then, maps=frozenset({m})), guards))
        return out


WRITES = ("set", "inc", "dec")


def _wrote(p: _Point, ins: Instruction) -> _Point:
    """The path past a write to a variable: tests on it from here on are the script's own."""
    dest = ins.args[0] if ins.name in WRITES and ins.args else None
    if not isinstance(dest, Value) or dest.table != "var" or str(dest) == STORY:
        return p
    return replace(p, written=p.written | {str(dest)})


def _reads(c: Condition) -> frozenset[str]:
    return frozenset(str(v) for t in c.terms for v in t.values if v.table == "var")


def _counted(p: _Point, ins: Instruction) -> _Point:
    """The counter values after a write to it: `inc` moves them on, `set` to a number pins them, anything else
    forgets them."""
    args = _args(ins)
    if not args or args[0] != STORY or p.story is None:
        return p
    if ins.name == "inc":
        return replace(p, story=frozenset(v + 1 for v in p.story))
    if ins.name == "set" and args[1] == "=" and isinstance(args[2], int):
        return replace(p, story=frozenset({args[2]}))
    return replace(p, story=None)


def _with_result(p: _Point, ins: Instruction, tested: int | None) -> _Point:
    """`store_result sys[n]` right after a `flag_test`: sys[n] holds that flag; any other write to sys[n] forgets it."""
    if (
        ins.name == "store_result"
        and isinstance(ins.args[0], Index)
        or ins.name == "set"
        and isinstance(ins.args[0], Value)
        and ins.args[0].table == "sys"
    ):
        n = ins.args[0].n
    else:
        return p
    kept = frozenset(r for r in p.results if r[0] != n)
    if ins.name == "store_result" and tested is not None:
        kept |= {(n, tested)}
    return replace(p, tested=None, results=kept)


def _flag_test(c: Condition, results: frozenset[tuple[int, int]]) -> int | None:
    """The flag a condition tests: exactly `sys.w[n] == 0` (or `!= 0`, or `sys.w[n]` alone: map 233's door) on a
    system variable holding a flag result."""
    if len(c.terms) != 1:
        return None
    term = c.terms[0]
    zero = len(term.values) == 2 and term.values[1].table == "imm" and term.values[1].n == 0
    if not (term.compare == 6 or term.compare in (0, 3) and zero):
        return None
    a = term.values[0]
    if a.table != "sys":
        return None
    return next((flag for n, flag in results if n == a.n), None)


@dataclass(frozen=True)
class SceneGraph:
    scene: int
    placements: frozenset[Op]
    arrivals: frozenset[Op]  # effects the setup runs itself, on arrival
    effects: dict[tuple[int, int], frozenset[Op]]  # by entry (kind, id), walked on the maps its placements cover

    def actions(self) -> set[Action]:
        return set(_actions(self.scene))

    def _placed(self) -> set[Action]:
        out = {Action(self.scene, a.maps, ARRIVE, a.name, a.args, a.guards) for a in self.arrivals}
        for p in self.placements:
            trigger, entry = _trigger(p)
            if trigger is None:
                continue
            for e in self.effects.get(entry, frozenset()):
                if e.maps & p.maps:
                    out.add(Action(self.scene, e.maps & p.maps, trigger, e.name, e.args, p.guards | e.guards))
        return _resolved(out | self._uses(out))

    def _uses(self, placed: set[Action]) -> set[Action]:
        """The A script's effects that need an item equipped, at the zones that set the variables it also reads (map
        129's gas: the zones set var.w[0xa], the Silex blows the wall)."""
        out = set()
        for e in self.effects.get(USE, frozenset()):
            item = _item(e.guards)
            if item is None:
                if e.zone is not None and e.name in ("flag_on", "flag_off"):  # a switch: A in its box (map 234's)
                    out.add(Action(self.scene, e.maps, Trigger("use", box=e.zone), e.name, e.args, e.guards))
                continue
            for box in _where(e, placed):
                out.add(Action(self.scene, e.maps, Trigger("use", box=box, item=item), e.name, e.args, e.guards))
        return out

    def exits(self) -> set[Exit]:
        """Map changes fired by stepping on a trigger."""
        return self._exits("step")

    def talk_exits(self) -> set[Exit]:
        """Map changes fired by talking to an actor (a boatman, a guide)."""
        return self._exits("talk")

    def _exits(self, kind: str) -> set[Exit]:
        out = set()
        for a in self.actions():
            if a.name in ("map_change", "map_change_continue") and a.trigger.kind == kind:
                to, how, x, y = a.args[:4]
                facing = a.args[4] if a.name == "map_change" else None
                out.add(Exit(self.scene, a.maps, a.trigger.box, to, how, x, y, facing, a.guards, a.trigger.actor))
        return out

    def steps(self) -> set[Step]:
        """Writes to the story counter, one per value the guards pin (`var.w[0x10] == v`, or a list of them)."""
        out = set()
        for a in self.actions():
            if not a.args or a.args[0] != STORY or a.name not in ("inc", "set") or not _allowed(a.guards):
                continue
            ats: list[int | None] = [*sorted(_pinned(a.guards))] or [_floor(a.guards)]
            for at in ats:
                to = _written(a, at)
                out.add(Step(self.scene, a.maps, at, to, a.trigger, a.guards))
        return out


@cache
def _actions(scene: int) -> frozenset[Action]:
    g = scene_graph(scene)
    return frozenset(g._placed())


def _resolved(actions: set[Action]) -> set[Action]:
    """One action for paths that differ by a test alone: `a && c` and `a && !c` make `a`. Paths that tested the counter apart reach an action with guards a meet would have dropped (map 79's
    door: through `flag[146]`, and through `!flag[146]` either side of `var.w[0x10] != 26`)."""
    groups: dict[Action, list[Action]] = {}
    for a in actions:
        groups.setdefault(replace(a, guards=frozenset()), []).append(a)
    out: set[Action] = set()
    for same in groups.values():
        out |= _folded(same)
    return out


def _folded(same: list[Action]) -> set[Action]:
    """Copies of one action folded until none fold: two whose guards differ by one test taken and not taken make one
    without it. A tighter copy stays beside a looser one: its guards may pin the counter (map 9's `inc` at 5)."""
    kept = set(same)
    while len(kept) > 1:
        halves: dict[tuple[frozenset[Guard], Condition], dict[bool, Action]] = {}
        pair = None
        for a in sorted(kept, key=str):
            for g in a.guards:
                side = halves.setdefault((a.guards - {g}, g.condition), {})
                side[g.holds] = a
                if len(side) == 2:
                    pair = (side[True], side[False])
                    break
            if pair:
                break
        if pair is None:
            return kept
        kept = (kept - set(pair)) | {replace(pair[0], guards=pair[0].guards & pair[1].guards)}
    return kept


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


def _floor(guards: frozenset[Guard]) -> int | None:
    """Too many values to pin, but a lower bound (`!(var.w[0x10] < 59)`): the counter only goes up, so the step is
    met first at that bound. None: no bound (0 allowed)."""
    allowed = _allowed(guards)
    low = min(allowed)
    return low if low > 0 else None


def _single(g: Guard) -> tuple[str, Callable[[int], bool]] | None:
    """A guard on one variable against a number: its name and the values it lets through."""
    terms = g.condition.terms
    if len(terms) != 1 or terms[0].compare not in COMPARE_TEST or len(terms[0].values) != 2:
        return None
    a, b = terms[0].values
    if b.table not in ("imm", "byte"):
        return None
    test, n = COMPARE_TEST[terms[0].compare], b.n
    return str(a), lambda v: test(v, n) == g.holds


def _item(guards: frozenset[Guard]) -> int | None:
    """The item a `use` needs: the one value its guards on var.w[0xc] let through, if they pin one."""
    for g in guards:
        single = _single(g)
        if single is not None and single[0] == ITEM:
            items = [v for v in range(0x400) if single[1](v)]
            if len(items) == 1:
                return items[0]
    return None


def _where(use: Op, placed: set[Action]) -> list[tuple[Arg, Arg, Arg, Arg] | None]:
    """Where the hero stands for a `use`: the step zones that set the other variables its guards read to a value
    they let through (None: anywhere on its maps, it reads no other)."""
    needs = [s for g in use.guards if (s := _single(g)) is not None and s[0] != ITEM and s[0].startswith("var")]
    if not needs:
        return [None]
    return sorted(
        {
            a.trigger.box
            for a in placed
            if a.trigger.kind == "step"
            and a.trigger.box is not None
            and a.maps & use.maps
            and a.name == "set"
            and any(
                a.args[0] == name and a.args[1] == "=" and isinstance(a.args[2], int) and ok(a.args[2])
                for name, ok in needs
            )
        },
        key=str,
    )


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
    if USE in addresses:
        effects[USE] = frozenset(_Walker(scene, data, EFFECTS).run(addresses[USE], maps))
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


def walled(g: SceneGraph, e: Exit) -> frozenset[Guard]:
    """The flag guards under which the map's setup walls the exit's box (`tile_attr_fill` of its cells, 0x40): map
    233's door to 235 shut unless the switch on 234 set flag 55. The exit needs them the other way."""
    if e.box is None:
        return frozenset()
    out = set()
    for a in g.actions():
        if a.trigger != ARRIVE or a.name not in WALL_OPS or not a.maps & e.maps or a.args[-1] != WALL:
            continue
        cells = a.args[:-1] if len(a.args) == 5 else (*a.args[:2], *a.args[:2])  # fill: x1 y1 x2 y2; set: x y
        if all(isinstance(v, int) for v in (*cells, *e.box)) and _covers(cells, e.box):
            out |= {Guard(f.condition, not f.holds, f.flag) for f in a.guards if f.flag is not None}
    return frozenset(out)


def walls(g: SceneGraph) -> list[dict[str, object]]:
    """The cells a map's setup opens under a story flag (`tile_attr_fill ..., 0` past `flag_test`): map 239's ways
    north, shut until the switches on 242 and 243. `flag` / `on`: the state that opens them."""
    out = []
    for a in g.actions():
        if a.trigger != ARRIVE or a.name not in WALL_OPS or a.args[-1] != 0:
            continue
        cells = a.args[:-1] if len(a.args) == 5 else (*a.args[:2], *a.args[:2])
        needs = [f for f in a.guards if f.flag is not None]
        if len(needs) == 1 and all(isinstance(v, int) for v in cells):
            out.append({"maps": sorted(a.maps), "box": list(cells), "flag": needs[0].flag, "on": needs[0].flag_on()})
    return out


def _covers(wall: tuple[Arg, ...], box: tuple[Arg, ...]) -> bool:
    x1, y1, x2, y2 = (int(v) for v in wall)
    bx1, by1, bx2, by2 = (int(v) for v in box)
    return x1 <= bx1 and y1 <= by1 and bx2 <= x2 and by2 <= y2


def _flags(guards: frozenset[Guard]) -> dict[str, bool] | None:
    """The story flags the guards need, on or off; None when they contradict (the path never runs)."""
    out: dict[str, bool] = {}
    for g in guards:
        on = g.flag_on()
        if on is None:
            continue
        if out.setdefault(str(g.flag), on) != on:
            return None
    return out


def _possible(guards: frozenset[Guard]) -> bool:
    return bool(_allowed(guards)) and _flags(guards) is not None


def openers(g: SceneGraph) -> set[Trigger]:
    """The triggers whose entry clears collision cells: a door the hero opens (map 123's, rammed three times)."""
    return {a.trigger for a in g.actions() if a.name in WALL_OPS and a.args[-1] == 0 and a.trigger != ARRIVE}


def gate_actions(g: SceneGraph) -> set[Action]:
    """Actors that open when talked to: their entry sets their own byte 1 bits 0-1 (map 126's cell gates)."""
    return {
        a
        for a in g.actions()
        if a.trigger.kind == "talk"
        and a.name == "actor_field_or"
        and a.args[:2] == (a.trigger.actor, 1)
        and isinstance(a.args[2], int)
        and a.args[2] & 3 == 3
    }


def flag_actions(g: SceneGraph) -> set[Action]:
    """The actions that turn a story flag on or off."""
    return {a for a in g.actions() if a.name in ("flag_on", "flag_off") and isinstance(a.args[0], int)}


def _trigger_data(t: Trigger) -> dict[str, object]:
    return {"kind": t.kind, "box": t.box and list(t.box), "actor": t.actor, "item": t.item}


def _counter(guards: frozenset[Guard]) -> list[int] | None:
    """The counter values the guards allow, None for any."""
    allowed = _allowed(guards)
    return None if allowed == COUNTER else sorted(allowed)


def _negated(guard: str) -> str | None:
    """`!(c)` for a single compare `c`: `c`; None for anything else."""
    body = guard[2:-1]
    simple = not any(op in body for op in ("&&", "||", "(", "flag["))
    return body if guard.startswith("!(") and guard.endswith(")") and simple else None


def _complement(exits: list[dict[str, Any]]) -> None:
    """Two exits on one box, one guarded by `!(a)`, `!(b)`, the other by nothing: the other runs when a or b holds.
    The guards keep what every path took, so the branch both `a` and `b` jump to loses them (map 179's edges: by
    `var.w[0x23]`, the map the hero came from). Give it `a || b` back."""
    boxes: dict[tuple[object, ...], list[dict[str, Any]]] = {}
    for e in exits:
        if e["box"] is not None:
            boxes.setdefault((e["scene"], tuple(e["maps"]), tuple(e["box"])), []).append(e)
    for pair in boxes.values():
        guarded = [e for e in pair if e["guards"]]
        if len(pair) != 2 or len(guarded) != 1:
            continue
        terms = [_negated(g) for g in guarded[0]["guards"]]
        if all(terms):
            next(e for e in pair if not e["guards"])["guards"] = [" || ".join(t for t in terms if t)]


def _entered(steps: list[dict[str, Any]], exits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """An arrival step with no counter value of its own takes the values of the exits into its map, when each of
    them has some: map 507's cutscene moves the counter to 111 on arrival, and only map 203's zone, at 93 or 109,
    leads there."""
    out = []
    for s in steps:
        into = [e["counter"] for e in exits if set(s["maps"]) & {e["to"]}]
        if s["at"] is not None or s["trigger"]["kind"] != "arrive" or not into or None in into:
            out.append(s)
            continue
        out += [{**s, "at": v} for v in sorted(set().union(*into))]
    return out


def export() -> dict[str, object]:
    """The graph as plain data: map scenes, exits, story steps and the actions that set story flags, each with the
    counter values it needs (`counter`, null for any), the flags (`flags`, {"n": on}) and its guards as text. Exit boxes are 16 px cells (inclusive), arrivals 8 px units."""
    gs = graphs()
    exits = [
        {
            "scene": e.scene,
            "maps": sorted(e.maps),
            "box": e.box and list(e.box),
            "actor": e.actor,
            "to": e.to,
            "kind": e.kind,
            "x": e.x,
            "y": e.y,
            "facing": e.facing,
            "counter": _counter(e.guards),
            "flags": _flags(e.guards | walled(g, e)),
            "guards": sorted(map(str, e.guards)),
        }
        for g in gs
        for e in g.exits() | g.talk_exits()
        if _possible(e.guards)
    ]
    _complement(exits)
    steps = [
        {
            "scene": s.scene,
            "maps": sorted(s.maps),
            "at": s.at,
            "to": s.to,
            "trigger": _trigger_data(s.trigger),
            "flags": _flags(s.guards),
            "guards": sorted(map(str, s.guards)),
        }
        for g in gs
        if g.scene != DEBUG_SCENE
        for s in g.steps()
        if _flags(s.guards) is not None
    ]
    steps = _entered(steps, exits)
    flags = [
        {
            "scene": a.scene,
            "maps": sorted(a.maps),
            "flag": a.args[0],
            "on": a.name == "flag_on",
            "trigger": _trigger_data(a.trigger),
            "counter": _counter(a.guards),
            "flags": _flags(a.guards),
            "guards": sorted(map(str, a.guards)),
            "opens": a.trigger in opens,
        }
        for g in gs
        if g.scene != DEBUG_SCENE
        for opens in [openers(g)]
        for a in flag_actions(g)
        if _possible(a.guards)
    ]
    items = [
        {
            "scene": a.scene,
            "maps": sorted(a.maps),
            "item": a.args[0],
            "trigger": _trigger_data(a.trigger),
            "counter": _counter(a.guards),
            "flags": _flags(a.guards),
            "guards": sorted(map(str, a.guards)),
        }
        for g in gs
        if g.scene != DEBUG_SCENE
        for a in g.actions()
        if a.name == "item_add" and isinstance(a.args[0], int) and a.trigger.kind != "use" and _possible(a.guards)
    ]
    gates = [
        {"scene": g.scene, "maps": sorted(a.maps), "actor": a.trigger.actor, "counter": _counter(a.guards)}
        for g in gs
        if g.scene != DEBUG_SCENE
        for a in gate_actions(g)
        if _possible(a.guards)
    ]
    order = lambda d: json.dumps(d, sort_keys=True)
    return {
        "scenes": {str(m): scene for m, scene in sorted(map_scenes().items())},
        "exits": sorted(exits, key=order),
        "steps": sorted(steps, key=order),
        "flags": sorted(flags, key=order),
        "items": sorted(items, key=order),
        "gates": sorted(gates, key=order),
        "walls": sorted((w for g in gs for w in walls(g)), key=order),
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
