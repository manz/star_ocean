"""Byte edits to scene event data (the VM scripts the scene table's first pointer holds), for puzzles the French
words change. Each edited scene is unpacked, checked, edited in place (same length, so the script's jump addresses
hold), packed back into a 0x81 container and written over the original one. Writes build/gen/scene_events/NN.bin
and build/gen/scene_events.i.

The game's own `unpack` reads event data, so it must stay in banks the bus maps: unlike scene text (sram_text.s),
it cannot move to ROM pages 6-7.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.dialog import SCENE_TABLE
from tools.encode_text import GEN, SCENE_RECORD, container
from tools.lz import decode
from tools.rom import Rom


@dataclass(frozen=True)
class Edit:
    offset: int  # in the unpacked event data
    old: bytes
    new: bytes
    why: str


EDITS: dict[int, list[Edit]] = {
    80: [
        # The door test after the console: set 4, then the slot picked for letters 1, 2 and 3 (the 4th is the slot
        # left). The French answer GAÏA picks "A I G A" slots 3, 1-or-4, 2, 4-or-1: letter 2's test becomes a
        # second `set == 4` so either A passes.
        Edit(0x3A7, bytes.fromhex("0080 4e00 01"), bytes.fromhex("0080 4c00 04"), "letter 2: either A"),
    ],
}


def event_pointer(rom: Rom, scene: int) -> int:
    return int.from_bytes(rom.read(SCENE_TABLE + (scene - 1) * SCENE_RECORD, 3), "little")


def edited(rom: Rom, scene: int, edits: list[Edit]) -> bytes:
    data = bytearray(decode(rom.read, event_pointer(rom, scene))[0])
    for e in edits:
        if len(e.old) != len(e.new):
            raise ValueError(f"scene {scene} {e.offset:#x}: an edit must keep the length")
        found = bytes(data[e.offset : e.offset + len(e.old)])
        if found != e.old:
            raise ValueError(f"scene {scene} {e.offset:#x}: expected {e.old.hex(' ')}, found {found.hex(' ')}")
        data[e.offset : e.offset + len(e.new)] = e.new
    return bytes(data)


def build(out: Path = GEN, edits: dict[int, list[Edit]] = EDITS) -> None:
    rom = Rom()
    (out / "scene_events").mkdir(parents=True, exist_ok=True)
    lines = []
    for scene, scene_edits in sorted(edits.items()):
        name = f"{scene:02d}.bin"
        packed = container(edited(rom, scene, scene_edits))
        pointer = event_pointer(rom, scene)
        room = decode(rom.read, pointer)[1]
        if len(packed) > room:
            raise ValueError(f"scene {scene}: the edited events pack to {len(packed)} bytes, the original has {room}")
        (out / "scene_events" / name).write_bytes(packed)
        lines += [
            f".alloc scene_events_{scene:02d} at 0x{pointer:06X} size {len(packed)} {{",
            f'    .incbin "scene_events/{name}"',
            "}",
        ]
    (out / "scene_events.i").write_text("\n".join(lines) + "\n", encoding="utf-8")
