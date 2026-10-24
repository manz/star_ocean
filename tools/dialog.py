"""Dialog text blocks: scene table E4:0000 -> LZ block -> u16 message offsets -> code streams.

Stream (C2:39DB): a code byte, bit 7 set -> 2 bytes ``(b0 & 0x7F) | b1 << 7``; ``5 <= code <= 0x4000`` is glyph
``code - 5``, the rest are the controls of ``text/so_dialog_ctl.tbl`` (handlers C2:3B2F[(code + 1) & 0xFF]).
Messages end in FFFF (end) or FFFE (rewind).
"""

from __future__ import annotations

from pathlib import Path

from katsuji.script import Table

from tools.lz import decode
from tools.rom import ROOT, Rom

# C6:10E0: 6-byte records per scene id (1-based): event-data LZ ptr (-> $7E:3100), text LZ ptr (-> $7E:B873).
SCENE_TABLE = 0xE40000
SCENES = 94

GLYPH_BASE = 5
GLYPHS = ROOT / "text" / "so_dialog.tbl"
CONTROLS = ROOT / "text" / "so_dialog_ctl.tbl"


def dialog_table() -> Table:
    table = Table(str(GLYPHS))
    table.include(str(CONTROLS))
    return table


def encode_code(code: int) -> bytes:
    return bytes([code]) if code < 0x80 else bytes([(code & 0x7F) | 0x80, code >> 7])


def glyphs(path: Path = GLYPHS) -> dict[int, str]:
    """``{glyph index: text}`` from the stream-keyed glyph table."""
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, text = line.split("=", 1)
        raw = bytes.fromhex(key)
        code = raw[0] if len(raw) == 1 else (raw[0] & 0x7F) | raw[1] << 7
        if encode_code(code) != raw:
            raise ValueError(f"bad key {key}")
        out[code - GLYPH_BASE] = text
    return out


def _u16(data: bytes, o: int) -> int:
    return data[o] | data[o + 1] << 8


def messages(block: bytes) -> list[bytes]:
    """Each message's bytes, from its offset up to the next one (terminator included)."""
    offsets = [_u16(block, i) for i in range(0, _u16(block, 0), 2)]
    if offsets != sorted(offsets):
        raise ValueError("message offsets out of order")
    ends = [*offsets[1:], len(block)]
    return [block[start:end] for start, end in zip(offsets, ends, strict=True)]


def build_block(values: list[bytes]) -> bytes:
    """Inverse of :func:`messages`: offset list then the messages back to back."""
    offset = 2 * len(values)
    header = bytearray()
    for value in values:
        header += offset.to_bytes(2, "little")
        offset += len(value)
    return bytes(header) + b"".join(values)


def scene_text_ptr(rom: Rom, scene: int) -> int:
    return int.from_bytes(rom.read(SCENE_TABLE + (scene - 1) * 6 + 3, 3), "little")


def scene_block(rom: Rom, scene: int) -> bytes:
    return decode(rom.read, scene_text_ptr(rom, scene))[0]
