"""Encoder for the scene event scripts tools.scene_script decodes: the same structures back to bytes, exactly (a
decoded scene re-encodes to its own bytes), and a small assembler with labels to write scripts from Python.

    code, labels = assemble([
        op("say_mode1", 9),
        "loop",
        op("wait", 1),
        op("goto", "loop"),
    ], base=0x1D)
"""

from __future__ import annotations

from collections.abc import Sequence

from tools.scene_script import (
    COMPARE,
    EXPR_OPS,
    JOIN,
    NAMES,
    OPS,
    STORES,
    Condition,
    Expression,
    Header,
    Index,
    Instruction,
    Jump,
    Operand,
    Operator,
    Term,
    Value,
)


def encode_index(i: Index) -> bytes:
    if not i.wide:
        if i.n >= 0x80:
            raise ValueError(f"index {i.n:#x} needs two bytes")
        return bytes([i.n])
    return bytes([0x80 | i.n >> 8, i.n & 0xFF])


def encode_value(v: Value) -> bytes:
    if v.table == "byte":
        return bytes([v.n]) if v.run is None else bytes([0xF0 | v.run, v.n])
    if v.table == "imm":
        return bytes([v.flags | v.size]) + v.n.to_bytes(v.size + 1, "little")
    t = 0x80 | (0x40 if v.table == "sys" else 0) | v.flags | v.size
    return bytes([t]) + encode_index(Index(v.n, v.wide))


def _encode_condition(c: Condition) -> bytes:
    out = bytearray()
    for i, term in enumerate(c.terms):
        out.append(term.compare)
        for v in term.values:
            out += encode_value(v)
        out.append(c.joiners[i] if i < len(c.joiners) else c.end)
    return bytes(out)


def _encode_expression(e: Expression) -> bytes:
    out = bytearray()
    for token in e.tokens:
        out += bytes([token.byte]) if isinstance(token, Operator) else encode_value(token)
    return bytes(out + b"\xff")


def _encode_operand(arg: Operand, base: int, labels: dict[str, int]) -> bytes:
    if isinstance(arg, Value):
        return encode_value(arg)
    if isinstance(arg, Index):
        return encode_index(arg)
    if isinstance(arg, Jump):
        target = labels[arg.target] if isinstance(arg.target, str) else arg.target
        return (target - base).to_bytes(2, "little")
    if isinstance(arg, Condition):
        return _encode_condition(arg)
    return _encode_expression(arg)


def encode(ins: Instruction, base: int, labels: dict[str, int] | None = None) -> bytes:
    """One instruction's bytes; `base` is the header length (jump words count from the header's end)."""
    if ins.name == "db":
        return ins.raw
    out = bytes([NAMES[ins.name]])
    return out + b"".join(_encode_operand(a, base, labels or {}) for a in ins.args)


def encode_header(head: Header) -> bytes:
    out = bytearray(head.length.to_bytes(2, "little") + b"\0\0")
    for e in head.entries:
        out += bytes([e.kind, e.id]) + e.address.to_bytes(2, "little")
    return bytes(out + b"\xff")


def assemble(items: Sequence[str | Instruction], base: int, origin: int | None = None) -> tuple[bytes, dict[str, int]]:
    """Strings are labels, the rest instructions; code starts at offset `origin` (default `base`, right after the
    header). Returns the bytes and each label's offset in the event data."""
    labels: dict[str, int] = {}
    at = base if origin is None else origin
    for item in items:
        if isinstance(item, str):
            labels[item] = at
        else:
            at += len(encode(item, base, dict.fromkeys(_jump_labels(item), base)))
    code = b"".join(encode(i, base, labels) for i in items if not isinstance(i, str))
    return code, labels


def _jump_labels(ins: Instruction) -> list[str]:
    return [a.target for a in ins.args if isinstance(a, Jump) and isinstance(a.target, str)]


# Builders: plain ints become the smallest immediate (or a one- or two-byte index), strings become jump labels.


def imm(n: int) -> Value:
    return Value("imm", n, max(0, (n.bit_length() - 1) // 8))


def var(index: int, size: int = 0) -> Value:
    return Value("var", index, size, wide=index >= 0x80)


def sys(index: int, size: int = 0) -> Value:
    return Value("sys", index, size, wide=index >= 0x80)


def _value(v: int | Value) -> Value:
    return v if isinstance(v, Value) else imm(v)


def term(a: int | Value, compare: str | None = None, b: int | Value | None = None) -> Term:
    """`term(var(0x4c), "==", 4)`, or `term(x)` for a truthy test."""
    if compare is None:
        return Term(6, (_value(a),))
    if b is None:
        raise ValueError("a comparison needs two values")
    return Term({s: n for n, s in COMPARE.items()}[compare], (_value(a), _value(b)))


def condition(*terms: Term, join: str = "&&") -> Condition:
    joiner = {s: n for n, s in JOIN.items()}[join]
    return Condition(terms, (joiner,) * (len(terms) - 1))


def assign(dest: Value, *tokens: int | str | Value, store: str = "=") -> Instruction:
    """`set dest <store> tokens` (RPN: ints and values push, "+", "-", ... apply)."""
    operators = {s: n for n, s in EXPR_OPS.items()}
    typed = Value(dest.table, dest.n, dest.size, dest.flags & ~0x38 | STORES.index(store) << 3, wide=dest.wide)
    expr = tuple(Operator(operators[t]) if isinstance(t, str) else _value(t) for t in tokens)
    return Instruction(0, 0, "set", [typed, Expression(expr)])


def op(name: str, *args: int | str | Operand) -> Instruction:
    spec = OPS[NAMES[name]][1]
    if len(args) != len(spec):
        raise ValueError(f"{name} takes {len(spec)} operands, got {len(args)}")
    return Instruction(0, 0, name, [_build(kind, a) for kind, a in zip(spec, args, strict=True)])


def _build(kind: str, arg: int | str | Operand) -> Operand:
    if kind == "j" and isinstance(arg, (int, str)):
        return Jump(arg)
    if kind in "mx" and isinstance(arg, int):
        return Index(arg, wide=arg >= 0x80)
    if kind == "v" and isinstance(arg, int):
        return imm(arg)
    if isinstance(arg, (int, str)):
        raise TypeError(f"operand kind {kind!r} cannot take {arg!r}")
    return arg
