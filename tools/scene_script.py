"""Disassembler for the scene event scripts: the VM at C2:1271 (opcode table C2:3769, indexed by opcode + 1).

Event data (scene record +0, LZ, unpacked to $7E:3100):

- header: u16 length, u16 0, then (kind, id, u16 address) trigger entries up to an FF. Addresses and jump operands
  are relative to the header's end.
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
from dataclasses import dataclass, field

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
    0x0F: ("op_0f", "v"),
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


@dataclass(frozen=True)
class Entry:
    kind: int
    id: int
    address: int  # relative to the header's end


@dataclass(frozen=True)
class Header:
    length: int
    entries: tuple[Entry, ...]


@dataclass
class Instruction:
    offset: int  # in the unpacked event data
    size: int
    name: str
    operands: list[str]
    targets: list[int] = field(default_factory=list)  # jump destinations, data offsets
    message: int | None = None


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

    def index(self) -> int:
        first = self.byte()
        return first if first < 0x80 else (first & 0x7F) << 8 | self.byte()

    def value(self) -> str:
        if self.run:
            self.run -= 1
            return str(self.byte())
        t = self.byte()
        if t >= 0xF0:
            self.run = t & 0x0F
            return str(self.byte())
        if t & 0x80:
            table = "sys" if t & 0x40 else "var"
            return f"{table}{SIZES[t & 3]}[{self.index():#x}]"
        return str(int.from_bytes(bytes(self.byte() for _ in range((t & 3) + 1)), "little"))

    def jump(self) -> int:
        return self.base + self.word()

    def expression(self, target: str, store: int) -> str:
        stack = [target]
        while (b := self.data[self.pos]) != 0xFF:
            if b & 0x3C:
                self.pos += 1
                stack.append(EXPR_OPS.get(b, f"op{b:02x}"))
            else:
                stack.append(self.value())
        self.pos += 1
        return f"{target} {STORES[store]} {' '.join(stack[1:])}"

    def condition(self) -> str:
        parts = []
        while True:
            compare = self.byte()
            if compare == 6:
                parts.append(self.value())
            else:
                a, b = self.value(), self.value()
                parts.append(f"{a} {COMPARE.get(compare, f'cmp{compare:02x}')} {b}")
            joiner = self.byte()
            if joiner not in JOIN:
                return " ".join(parts)
            parts.append(JOIN[joiner])


def instruction(data: bytes, pos: int, base: int) -> Instruction:
    op = data[pos]
    if op not in OPS:
        raise ValueError(f"unknown opcode {op:#04x} at {pos:#x}")
    name, spec = OPS[op]
    r = Reader(data, pos + 1, base)
    ins = Instruction(pos, 0, name, [])
    for kind in spec:
        _operand(r, kind, ins)
    ins.size = r.pos - pos
    return ins


def _operand(r: Reader, kind: str, ins: Instruction) -> None:
    if kind == "v":
        ins.operands.append(r.value())
    elif kind == "j":
        target = r.jump()
        ins.targets.append(target)
        ins.operands.append(label(target))
    elif kind == "m":
        ins.message = r.index()
        ins.operands.append(str(ins.message))
    elif kind == "x":
        ins.operands.append(f"sys[{r.index():#x}]")
    elif kind == "c":
        ins.operands.append(r.condition())
    else:  # e: the expression runs over the value just read (pushed first) and stores into it
        store = (r.data[ins.offset + 1] >> 3) & 7
        ins.operands[-1] = r.expression(ins.operands[-1], store)


def label(offset: int) -> str:
    return f"L{offset:04x}"


def disassemble(data: bytes) -> tuple[Header, list[Instruction]]:
    """Linear sweep over the whole code area: scripts sit back to back. A stray end byte (0x80, scenes
    STRAY_TAIL_SCENES) is kept as `db`."""
    head = header(data)
    out, pos = [], head.length
    while pos < len(data):
        if data[pos] not in OPS:
            out.append(Instruction(pos, len(data) - pos, "db", [data[pos:].hex(" ")]))
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
    """French first lines by message index (the XML ids are the message index - 1)."""
    path = ROOT / "text" / "fr" / f"scene_{scene:02d}.xml"
    if not path.exists():
        return {}
    texts = {}
    for node in ET.parse(path).getroot():
        text = re.sub(r"\[[^]]*\]", " ", node.text or "").split("\n")
        first = next((line.strip() for line in text if line.strip()), "")
        texts[int(node.attrib["id"]) + 1] = first
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
    text = f"  ; {messages[ins.message]}" if ins.message in messages else ""
    return f"  {ins.offset:04x}{raw}  {ins.name} {', '.join(ins.operands)}".rstrip() + text


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
