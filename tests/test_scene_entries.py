"""What fires a scene's header entries, played in the patched game from a real arrival (tests/warp.py,
notes/text/scene_triggers.md).

- kind 0, id n: A pressed facing actor n. C2:03FC finds the active actor in the box in front of the hero, then
  C2:04D2 loads `$E613 + n * 2` into the pc; a zero entry falls through to the A script (C8:0000).
- kind 2, id 0x7F: A pressed with no actor in front: C8:0000 pushes the pc and jumps to `$E911`.
- kind 2, other ids: the hero stepping into a `trigger_zone` (op 22).

Laponia (map 22, scene 9) gives each villager its line as entry (0, n): woman 18 says message 8 from entry
(0, 0x12) at 0x289; its south exit is `trigger_zone 40, 55, 45, 55, 1`, entry (2, 1) changing to map 39. Zone corners count 16 px
cells, like the attribute grid `$EE73` (C6:4182 halves the 8 px tile before C6:54BB compares), not the 8 px
tiles of `map_change`.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from tests.screens import tap
from tests.warp import field, run_script, walk, warp
from tools.scene_asm import op

if TYPE_CHECKING:
    from kintsuki import Emu

PC = 0x7E0238
MAP = 0x7E043D
FIELD_STATE = 0x7E048A  # 2 once the arrival's name banner is gone; A only closes the banner before
TALK_ENTRIES = 0x7EE613  # kind 0 slice
WOMAN = 18  # npc_create 18, 40, 16 in Laponia
WOMAN_ENTRY = 0x3100 + 0x49 + 0x289  # scene 9: header 0x49 bytes, entry (0, 0x12)
A_SCRIPT = 0xC80000
A_ENTRY = 0x7EE911  # kind 2, id 0x7F
CONSOLE_A = 0x3100 + 0x1D + 0xA1  # scene 80: header 0x1d bytes, entry (2, 0x7F)
SETTLE = 60


@pytest.fixture(scope="module")
def game() -> Iterator[tuple[Emu, bytes]]:
    emu = field("fantasyanime_4")
    yield emu, emu.save_state()


def _arrive(game: tuple[Emu, bytes], map_id: int, x: int, y: int, facing: int) -> Emu:
    emu, start = game
    emu.load_state(start)
    warp(emu, map_id, x, y, facing)
    emu.run_frames(SETTLE)
    return emu


def _woman(game: tuple[Emu, bytes]) -> Emu:
    """Below the woman of Laponia, facing her, the banner gone."""
    emu = _arrive(game, 22, 40, 18, 0)
    assert emu.read(FIELD_STATE) == 2
    return emu


def _talk(emu: Emu) -> tuple[list[int], list[int], int]:
    """A pressed: (words written into the VM pc, kind 0 slice addresses read, A script runs)."""
    from kintsuki import CB_EXEC, CB_READ, CB_WRITE

    pcs: list[int] = []
    reads: list[int] = []
    runs: list[int] = []

    low = [0]

    def pc_written(address: int, value: int) -> None:  # called before the byte lands, low byte first
        if address == PC:
            low[0] = value
        else:
            pcs.append(low[0] | value << 8)

    handles = [
        (CB_WRITE, emu.add_write_callback(PC, PC + 1, pc_written)),
        (CB_READ, emu.add_read_callback(TALK_ENTRIES, TALK_ENTRIES + 0xFF, lambda a, _v: reads.append(a))),
        (CB_EXEC, emu.add_exec_callback(A_SCRIPT, A_SCRIPT, lambda a, _v: runs.append(a))),
    ]
    tap(emu, "A")
    for kind, handle in handles:
        emu.remove_callback(kind, handle)
    return pcs, reads, len(runs)


def test_talking_to_an_actor_reads_its_kind_0_entry(game: tuple[Emu, bytes]) -> None:
    _, reads, _ = _talk(_woman(game))
    assert reads == [TALK_ENTRIES + WOMAN * 2, TALK_ENTRIES + WOMAN * 2 + 1]


def test_talking_to_an_actor_runs_its_entry(game: tuple[Emu, bytes]) -> None:
    pcs, _, runs = _talk(_woman(game))
    assert (WOMAN_ENTRY in pcs, runs) == (True, 0)


def test_the_talked_actor_is_kept_in_2033(game: tuple[Emu, bytes]) -> None:
    emu = _woman(game)
    _talk(emu)
    assert emu.read16(0x7E2033) == 0x2000 + WOMAN * 0x40


def test_an_actor_without_an_entry_falls_to_the_a_script(game: tuple[Emu, bytes]) -> None:
    emu = _woman(game)
    emu.write_range(TALK_ENTRIES + WOMAN * 2, b"\0\0")
    pcs, _, runs = _talk(emu)
    assert (WOMAN_ENTRY in pcs, runs) == (False, 1)


def test_a_with_nothing_in_front_runs_entry_2_7f(game: tuple[Emu, bytes]) -> None:
    emu = _arrive(game, 164, 8, 8, 2)  # scene 80's console room
    walk(emu, "RIGHT", 16)
    walk(emu, "UP", 2)
    pcs, _, runs = _talk(emu)
    assert (emu.read16(A_ENTRY), CONSOLE_A in pcs, runs) == (CONSOLE_A, True, 1)


def test_stepping_into_a_trigger_zone_runs_its_entry(game: tuple[Emu, bytes]) -> None:
    emu = _arrive(game, 22, 85, 106, 2)  # 16 px cell (42, 53), two above the zone
    walk(emu, "DOWN", 24)
    emu.run_frames(150)
    assert emu.read16(MAP) == 39


def test_a_zone_turned_off_does_nothing(game: tuple[Emu, bytes]) -> None:
    emu = _arrive(game, 22, 85, 106, 2)  # 16 px cell (42, 53), two above the zone
    run_script(emu, [op("trigger_zone_off", 40, 55, 45, 55)], 2)
    walk(emu, "DOWN", 24)
    emu.run_frames(150)
    assert emu.read16(MAP) == 22
