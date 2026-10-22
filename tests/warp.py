"""Reach any map the way a door does: a save loads into the field, then one injected `op 24` (map change) runs in
the scene VM, so the map, its scene's event data and its start-up load as on a real arrival
(notes/text/scene_triggers.md).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tests.screens import emulator, tap
from tools.scene_asm import assemble, op

if TYPE_CHECKING:
    from kintsuki import Emu

SAVES = Path(__file__).parent / "saves"
EVENTS = 0x7E3100  # the unpacked scene event data
VM_PC, VM_WAIT, VM_OFF = 0x7E0238, 0x7E0234, 0x7E0231
VARS = 0x7EFEC3
LOADED = 300  # frames after the load screen's "Oui" for the field to run
ARRIVED = 150  # frames for the fade out, the map load and the fade in


def field(save: str) -> Emu:
    """tests/saves/<save>.srm loaded from its last saved slot, in the field."""
    emu = emulator("load_screen", (SAVES / f"{save}.srm").read_bytes()[:0x2000])
    tap(emu, "A,A")
    emu.run_frames(LOADED)
    return emu


def set_var(emu: Emu, index: int, value: int) -> None:
    """var.w[index]."""
    emu.write_range(VARS + index, value.to_bytes(2, "little"))


def warp(emu: Emu, map_id: int, x: int, y: int, facing: int) -> None:
    """Map change to `map_id` at tile (x, y) in 8 px units, as `op 24 map, 0, x, y, facing`."""
    base = emu.read16(EVENTS)
    origin = base + 0x40  # inside the old scene's start-up, which the map change leaves anyway
    code, _ = assemble([op("op_24", map_id, 0, x, y, facing), "idle", op("wait", 1), op("goto", "idle")], base, origin)
    emu.write_range(EVENTS + origin, code)
    emu.write_range(VM_PC, (0x3100 + origin).to_bytes(2, "little"))
    emu.write(VM_WAIT, 1)
    emu.write(VM_OFF, 0)
    emu.run_frames(ARRIVED)


def walk(emu: Emu, button: str, frames: int) -> None:
    """Hold a direction (kintsuki.Button name) for `frames`, then let the step end."""
    from kintsuki import Button

    emu.press(0, getattr(Button, button), True)
    emu.run_frames(frames)
    emu.press(0, getattr(Button, button), False)
    emu.run_frames(12)


def press(emu: Emu, buttons: str, tries: int = 4) -> None:
    """Tap each of the comma-separated buttons; an A is tapped again until the scene VM moves on (a message still
    typing ignores it), the cursor moves as they come."""
    for button in filter(None, buttons.split(",")):
        pc = emu.read16(VM_PC)
        for _ in range(tries if button == "A" else 1):
            tap(emu, button)
            if emu.read16(VM_PC) != pc:
                break


def press_until(emu: Emu, offset: int, frames: int = 3000) -> None:
    """Run until the scene VM rests at `offset` in the event data, tapping A only when it has sat still a while
    elsewhere (a message waiting on its window)."""
    still, pc = 0, emu.read16(VM_PC)
    for _ in range(frames // 10):
        emu.run_frames(10)
        now = emu.read16(VM_PC)
        still = still + 10 if now == pc else 0
        pc = now
        if pc - (EVENTS & 0xFFFF) == offset and still >= 60:
            return
        if pc - (EVENTS & 0xFFFF) != offset and still >= 120:
            tap(emu, "A")
            still = 0
    raise AssertionError(f"the scene VM never rested at {offset:#x}")
