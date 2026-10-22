"""Disassembler for the scene event scripts: the VM at C2:1271 (opcode table C2:3769, indexed by opcode + 1).

Event data (scene record +0, LZ, unpacked to $7E:3100):

- header: u16 length, u16 start-up offset (0 everywhere), then (kind, id, u16 address) trigger entries up to an FF.
  Addresses and jump operands are relative to the header's end (notes/text/scene_triggers.md).
- the code right after the header is the scene's start-up: it calls the setup (which branches on `sys.w[0xc]`, the
  map id) then loops on `wait 1`.
- code: an opcode byte, then its operands.

Operand value (C2:310C), by its first byte `t`:

- F0-FF: the next `t & 0x0F` values are bare bytes, this one is the byte after `t`.
- bit 7 set: a variable, `t & 0x40` picks the system table (C2:383F, 24-bit pointers) over $7E:FEC3. The index is
  one byte, or two (15 bits, big end first) when its first byte has bit 7. `t & 3` is the size (byte, word, long,
  dword).
- else an immediate of `(t & 3) + 1` bytes.

`set` (01) is a variable then an RPN expression up to an FF, run on a stack that starts with the variable's value;
bits 3-5 of the variable's type pick the final store (`=`, `+=`, ...). `if` (07) is two jump words (then, else) and a condition list:
comparator, values, joiner (00 or, 01 and, FF end).

    uv run python -m tools.scene_script 80 [--edited] [--bytes]
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass

from tools.lz import decode
from tools.rom import ROOT, Rom
from tools.scene_events import EDITS, edited, event_pointer

SIZES = ("", ".w", ".l", ".d")
STORES = ("=", "+=", "-=", "*=", "/=", "|=", "&=", "?=")  # C2:16DD by type bits 3-5
EXPR_OPS = {4: "+", 5: "-", 6: "*", 7: "/", 8: "|", 9: "&", 0x0A: "++", 0x0B: "--", 0x0C: "drop"}  # C2:16A7
COMPARE = {0: "==", 1: ">", 2: "<", 3: "!=", 4: ">=", 5: "<="}  # C2:18FE; 6 tests one value
JOIN = {0: "||", 1: "&&"}
STRAY_TAIL_SCENES = [2, 52, 76]  # scenes whose data ends in a stray byte

# opcode: (name, operands). v value, j jump, m message, x system index, c condition list, e expression.
# Named where the handler is read: say* set the window mode then the message; wait yields frames; choose opens the
# choice window and yields; actor_get, flag_test and the like leave a result ($0278) that store_result writes;
# wait_text re-runs itself until the window is done. op_NN are not read yet.
OPS: dict[int, tuple[str, str]] = {
    0x00: ("nop", ""),
    0x01: ("set", "ve"),
    0x02: ("inc", "v"),
    0x03: ("dec", "v"),
    0x04: ("goto", "j"),
    0x05: ("call", "j"),
    0x06: ("ret", ""),
    0x07: ("if", "jjc"),
    0x08: ("op_08", "vvvvvvv"),
    0x09: ("nop_09", ""),
    0x0A: ("op_0a", "vvvvv"),
    0x0B: ("op_0b", "vvv"),
    0x0C: ("op_0c", "vvvvv"),
    0x0D: ("say", "m"),
    0x0E: ("say_mode0", "m"),
    0x0F: ("syscall", "v"),
    0x10: ("op_10", "vvvv"),
    0x11: ("op_11", "vvvv"),
    0x12: ("op_12", "vv"),
    0x13: ("wait", "v"),
    0x14: ("nop_14", ""),
    0x15: ("op_15", "vv"),
    0x16: ("nop_16", ""),
    0x17: ("op_17", "vvv"),
    0x18: ("op_18", "v"),
    0x19: ("op_19", "vvvv"),
    0x1A: ("store_result", "x"),
    0x1B: ("nop_1b", ""),
    0x1C: ("op_1c", "v"),
    0x1D: ("op_1d", "vvv"),
    0x1E: ("op_1e", "vv"),
    0x1F: ("op_1f", "vvvv"),
    0x20: ("op_20", "vvvvvv"),
    0x21: ("op_21", "vvv"),
    0x22: ("op_22", "vvvvv"),
    0x23: ("nop_23", ""),
    0x24: ("op_24", "vvvvv"),
    0x25: ("say_mode1", "m"),
    0x26: ("op_26", "vvvv"),
    0x27: ("nop_27", ""),
    0x28: ("nop_28", ""),
    0x29: ("op_29", "vvv"),
    0x2A: ("op_2a", "vvv"),
    0x2B: ("op_2b", "v" * 14),
    0x2C: ("op_2c", "vv"),
    0x2D: ("op_2d", ""),
    0x2E: ("op_2e", ""),
    0x2F: ("op_2f", "vvv"),
    0x30: ("choose", "vv"),
    0x31: ("flag_on", "v"),
    0x32: ("flag_off", "v"),
    0x33: ("flag_test", "v"),
    0x34: ("op_34", ""),
    0x35: ("actor_get", "vv"),
    0x36: ("op_36", "vv"),
    0x37: ("op_37", "vvvv"),
    0x38: ("op_38", "vv"),
    0x39: ("say_mode8", "m"),
    0x3A: ("op_3a", "vvv"),
    0x3B: ("op_3b", "vvvvv"),
    0x3C: ("say_mode9", "m"),
    0x3D: ("nop_3d", ""),
    0x3E: ("nop_3e", ""),
    0x3F: ("nop_3f", ""),
    0x40: ("nop_40", ""),
    0x41: ("nop_41", ""),
    0x42: ("nop_42", ""),
    0x43: ("op_43", "vv"),
    0x44: ("nop_44", ""),
    0x45: ("op_45", "v"),
    0x46: ("op_46", "v"),
    0x47: ("op_47", "v"),
    0x48: ("nop_48", ""),
    0x49: ("op_49", "v"),
    0x4A: ("op_4a", "vv"),
    0x4B: ("op_4b", "vv"),
    0x4C: ("op_4c", "vv"),
    0x4D: ("op_4d", "vv"),
    0x4E: ("wait_text", ""),
    0x4F: ("op_4f", "v"),
    0x50: ("nop_50", ""),
    0x51: ("op_51", "v"),
    0x52: ("op_52", "vv"),
    0x53: ("op_53", "v"),
    0x54: ("op_54", "vv"),
    0x55: ("op_55", "v"),
    0x56: ("op_56", "vvv"),
    0x57: ("op_57", "v"),
    0x58: ("op_58", "v"),
    0x59: ("op_59", "v"),
    0x5A: ("op_5a", "v"),
    0x5B: ("flag2_test", "v"),
    0x5C: ("nop_5c", ""),
    0x5D: ("op_5d", "vvv"),
    0x5E: ("op_5e", "vvv"),
    0x5F: ("op_5f", "vv"),
    0x60: ("op_60", "vvvv"),
    0x61: ("op_61", "vv"),
    0x62: ("op_62", "v"),
    0x63: ("op_63", "vvv"),
    0x64: ("op_64", "vvvv"),
    0x65: ("op_65", "vv"),
    0x66: ("op_66", "vv"),
    0x67: ("op_67", "vvv"),
    0x68: ("op_68", "vvv"),
    0x69: ("op_69", "vv"),
    0xFF: ("end", ""),
}


# op 0F services (C2:8B4C), by number: notes/text/scene_syscalls.md has what each does and how sure.
SYSCALLS: tuple[str, ...] = (
    "nop",
    "actor_vanish",
    "actor_appear",
    "actor_vanish_b",
    "actor_appear_b",
    "palette_fade_build",
    "palette_fade_build_alt",
    "palette_fade_play",
    "screen_shake",
    "screen_shake_stop",
    "give_actor_item",
    "give_item",
    "effect_preset",
    "obj_frame_load",
    "obj_frame_load_wide",
    "obj_sheet_load",
    "special",
    "fx_channel_a",
    "fx_channel_b",
    "take_item",
    "add_fol",
    "actor_jump",
    "actor_in_box",
    "actor_fade_out",
    "actor_vanish_shake",
    "screen_set_main_sub",
    "screen_set_window_main_sub",
    "text_window_force_pos",
    "actor_set_move_bounds",
    "hero_force_run",
    "party_heal_living",
    "party_heal_all",
    "vram_load_sdd1",
    "vram_restore",
    "vram_save",
    "cgram_load_7f",
    "cgram_load_palette",
    "bg_freeze",
    "bg_unfreeze",
    "bg_set_scroll",
    "color_math_set",
    "palette_buffer_tint",
    "screen_close_effect_frame",
    "party_member_set_away",
    "party_member_clear_away",
    "sin",
    "cos",
    "sound_source_set_tile",
    "walk_slow_on",
    "walk_slow_off",
    "spawn_attr_0",
    "spawn_attr_2",
    "spawn_attr_3",
    "actor_spawn_icon_copy",
    "leader_spawn_get_icon",
    "ambient_event_roll",
    "set_param_block",
    "party_bond_inc",
    "scroll_wave",
    "party_remove_member",
    "roster_count",
    "party_count_active",
    "party_get_ids",
    "set_mosaic",
    "party_damage_all",
    "palette_buffer_op",
    "map_flags_set",
    "map_flags_clear",
    "sdd1_dma_to_wram",
    "flag2_on",
    "inventory_drop_type12",
    "battle_no_game_over",
    "keep_sound_on_next_map",
    "party_restore_hp",
    "party_restore_mp",
    "party_add_sp",
    "inventory_stash",
    "inventory_keep_key_items",
    "inventory_unstash",
    "party_solo",
    "party_restore_solo",
    "char_restore_hp",
    "char_restore_mp",
    "set_var15",
    "get_party_specialty_0a",
    "sound_signal",
    "display_reset",
    "mark_game_cleared",
    "get_game_cleared",
    "count_ladies_first",
    "party_hp_to_1",
    "char_learn",
    "remove_items_1ee_1f1",
    "flag2_clear",
)


@dataclass(frozen=True)
class Entry:
    kind: int
    id: int
    address: int  # relative to the header's end


@dataclass(frozen=True)
class Header:
    length: int
    entries: tuple[Entry, ...]


@dataclass(frozen=True)
class Value:
    """One operand value with its exact encoding: the type byte's other bits and the index width survive."""

    table: str  # imm, var, sys, or byte (bare: an F0-FF run's head or one of the bytes it covers)
    n: int  # the number, or the variable's index
    size: int = 0  # t & 3: byte, word, long, dword
    flags: int = 0  # the type byte's bits besides table and size (`set`'s store in bits 3-5)
    run: int | None = None  # on a run head: how many bare bytes follow
    wide: bool = False  # index in two bytes

    def __str__(self) -> str:
        if self.table in ("var", "sys"):
            return f"{self.table}{SIZES[self.size]}[{self.n:#x}]"
        return str(self.n)


@dataclass(frozen=True)
class Index:
    """A message number (op `m`) or a system variable index (op `x`)."""

    n: int
    wide: bool = False


@dataclass(frozen=True)
class Jump:
    target: int | str  # offset in the unpacked event data, or a label while assembling


@dataclass(frozen=True)
class Operator:
    byte: int  # an expression token with bits 2-5 set

    def __str__(self) -> str:
        return EXPR_OPS.get(self.byte, f"op{self.byte:02x}")


@dataclass(frozen=True)
class Expression:
    tokens: tuple[Value | Operator, ...]


@dataclass(frozen=True)
class Term:
    compare: int
    values: tuple[Value, ...]  # one for compare 6, else two

    def __str__(self) -> str:
        if self.compare == 6:
            return str(self.values[0])
        a, b = self.values
        return f"{a} {COMPARE.get(self.compare, f'cmp{self.compare:02x}')} {b}"


@dataclass(frozen=True)
class Condition:
    terms: tuple[Term, ...]
    joiners: tuple[int, ...]  # between terms: 00 or, 01 and
    end: int = 0xFF

    def __str__(self) -> str:
        parts = [str(self.terms[0])]
        for joiner, term in zip(self.joiners, self.terms[1:], strict=True):
            parts += [JOIN[joiner], str(term)]
        return " ".join(parts)


Operand = Value | Index | Jump | Expression | Condition


@dataclass
class Instruction:
    offset: int  # in the unpacked event data
    size: int
    name: str
    args: list[Operand]
    raw: bytes = b""  # a `db`'s bytes

    @property
    def targets(self) -> list[int]:
        return [a.target for a in self.args if isinstance(a, Jump) and isinstance(a.target, int)]

    @property
    def message(self) -> int | None:
        return self.args[0].n if self.name.startswith("say") and isinstance(self.args[0], Index) else None

    @property
    def operands(self) -> list[str]:
        if self.name == "db":
            return [self.raw.hex(" ")]
        if self.name == "set":
            dest, expr = self.args
            assert isinstance(dest, Value) and isinstance(expr, Expression)
            return [f"{dest} {STORES[(dest.flags >> 3) & 7]} {' '.join(map(str, expr.tokens))}"]
        spec = OPS[NAMES[self.name]][1]
        return [_text(kind, a) for kind, a in zip(spec, self.args, strict=True)]


NAMES = {name: op for op, (name, _) in OPS.items()}


def _text(kind: str, arg: Operand) -> str:
    if isinstance(arg, Jump):
        return label(arg.target) if isinstance(arg.target, int) else arg.target
    if isinstance(arg, Index):
        return f"sys[{arg.n:#x}]" if kind == "x" else str(arg.n)
    return str(arg)


def header(data: bytes) -> Header:
    length = int.from_bytes(data[0:2], "little")
    entries, i = [], 4
    while data[i] != 0xFF:
        entries.append(Entry(data[i], data[i + 1], int.from_bytes(data[i + 2 : i + 4], "little")))
        i += 4
    if i != length - 1:
        raise ValueError(f"header ends at {i:#x}, length says {length:#x}")
    return Header(length, tuple(entries))


class Reader:
    """Operand decoding over one instruction; the F0-FF run count lasts the instruction (C2:1273 clears it)."""

    def __init__(self, data: bytes, pos: int, base: int) -> None:
        self.data, self.pos, self.base, self.run = data, pos, base, 0

    def byte(self) -> int:
        b = self.data[self.pos]
        self.pos += 1
        return b

    def word(self) -> int:
        return self.byte() | self.byte() << 8

    def index(self) -> Index:
        first = self.byte()
        return Index(first) if first < 0x80 else Index((first & 0x7F) << 8 | self.byte(), wide=True)

    def value(self) -> Value:
        if self.run:
            self.run -= 1
            return Value("byte", self.byte())
        t = self.byte()
        if t >= 0xF0:
            self.run = t & 0x0F
            return Value("byte", self.byte(), run=self.run)
        if t & 0x80:
            i = self.index()
            return Value("sys" if t & 0x40 else "var", i.n, t & 3, t & 0x3C, wide=i.wide)
        n = int.from_bytes(bytes(self.byte() for _ in range((t & 3) + 1)), "little")
        return Value("imm", n, t & 3, t & 0x7C)

    def jump(self) -> Jump:
        return Jump(self.base + self.word())

    def expression(self) -> Expression:
        tokens: list[Value | Operator] = []
        while (b := self.data[self.pos]) != 0xFF:
            if b & 0x3C:
                self.pos += 1
                tokens.append(Operator(b))
            else:
                tokens.append(self.value())
        self.pos += 1
        return Expression(tuple(tokens))

    def condition(self) -> Condition:
        terms: list[Term] = []
        joiners: list[int] = []
        while True:
            compare = self.byte()
            terms.append(Term(compare, (self.value(),) if compare == 6 else (self.value(), self.value())))
            joiner = self.byte()
            if joiner not in JOIN:
                return Condition(tuple(terms), tuple(joiners), joiner)
            joiners.append(joiner)


def instruction(data: bytes, pos: int, base: int) -> Instruction:
    op = data[pos]
    if op not in OPS:
        raise ValueError(f"unknown opcode {op:#04x} at {pos:#x}")
    name, spec = OPS[op]
    r = Reader(data, pos + 1, base)
    args = [_operand(r, kind) for kind in spec]
    return Instruction(pos, r.pos - pos, name, args)


def _operand(r: Reader, kind: str) -> Operand:
    readers: dict[str, Callable[[], Operand]] = {
        "v": r.value,
        "j": r.jump,
        "m": r.index,
        "x": r.index,
        "c": r.condition,
        "e": r.expression,
    }
    return readers[kind]()


def label(offset: int) -> str:
    return f"L{offset:04x}"


def disassemble(data: bytes) -> tuple[Header, list[Instruction]]:
    """Linear sweep over the whole code area: scripts sit back to back. A stray end byte (0x80, scenes
    STRAY_TAIL_SCENES) is kept as `db`."""
    head = header(data)
    out, pos = [], head.length
    while pos < len(data):
        if data[pos] not in OPS:
            out.append(Instruction(pos, len(data) - pos, "db", [], data[pos:]))
            break
        ins = instruction(data, pos, head.length)
        out.append(ins)
        pos += ins.size
    return head, out


def scene_data(scene: int, with_edits: bool = False) -> bytes:
    rom = Rom()
    if with_edits and scene in EDITS:
        return edited(rom, scene, EDITS[scene])
    return decode(rom.read, event_pointer(rom, scene))[0]


def scene_messages(scene: int) -> dict[int, str]:
    """French first lines by message index (the XML id)."""
    path = ROOT / "text" / "fr" / f"scene_{scene:02d}.xml"
    if not path.exists():
        return {}
    texts = {}
    for node in ET.parse(path).getroot():
        text = re.sub(r"\[[^]]*\]", " ", node.text or "").split("\n")
        first = next((line.strip() for line in text if line.strip()), "")
        texts[int(node.attrib["id"])] = first
    return texts


def listing(data: bytes, messages: dict[int, str], show_bytes: bool = False) -> list[str]:
    head, code = disassemble(data)
    names = {head.length + e.address: f"entry {e.kind} {e.id:#04x}" for e in head.entries}
    targets = {t for ins in code for t in ins.targets} | set(names)
    lines = [f"; header {head.length:#x} bytes, {len(head.entries)} entries"]
    for ins in code:
        if ins.offset in targets:
            lines.append("")
            lines.append(f"{label(ins.offset)}:" + (f"  ; {names[ins.offset]}" if ins.offset in names else ""))
        lines.append(_line(data, ins, messages, show_bytes))
    return lines


def _line(data: bytes, ins: Instruction, messages: dict[int, str], show_bytes: bool) -> str:
    raw = f" {data[ins.offset : ins.offset + ins.size].hex(' '):<30}" if show_bytes else ""
    text = f"  ; {messages[ins.message]}" if ins.message in messages else _syscall(ins)
    return f"  {ins.offset:04x}{raw}  {ins.name} {', '.join(ins.operands)}".rstrip() + text


def _syscall(ins: Instruction) -> str:
    arg = ins.args[0] if ins.name == "syscall" else None
    if isinstance(arg, Value) and arg.table == "imm" and arg.n < len(SYSCALLS):
        return f"  ; {SYSCALLS[arg.n]}"
    return ""


def main(argv: list[str] | None = None, echo: Callable[[str], None] = print) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scene", type=int)
    parser.add_argument("--edited", action="store_true", help="with tools.scene_events edits applied")
    parser.add_argument("--bytes", action="store_true", help="show each instruction's bytes")
    args = parser.parse_args(argv)
    data = scene_data(args.scene, args.edited)
    for line in listing(data, scene_messages(args.scene), args.bytes):
        echo(line)


if __name__ == "__main__":
    main()
