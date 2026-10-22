"""Names by id (src/engine/name_index.s): the run table finds the entry the original scan of D7:06FA finds."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.screens import IPS, power_on
from tools.rom import Rom

IDS, COUNT = 0xD706FA, 893
SITES = (0xC03FBC, 0xC040BF, 0xC041F1, 0xC049CF, 0xCABE03)
SCAN = bytes.fromhex("a0 00 00 c2 20 b9 fa 06 f0 08 c5 20 f0 08 c8 c8 80 f3 7a ab 28 6b")
MISS = 0xFFFF
KEPT_X = 0x1234
Find = Callable[[int], tuple[int, int, int]]


def scan_ids() -> list[int]:
    rom = Rom()
    return [int.from_bytes(rom.read(IDS + 2 * i, 2), "little") for i in range(COUNT)]


def test_the_readers_are_the_scan_the_module_replaces() -> None:
    rom = Rom()
    assert all(rom.read(site, len(SCAN)) == SCAN for site in SITES)


def test_ids_appear_once() -> None:
    ids = scan_ids()
    assert len(set(ids)) == COUNT


@pytest.fixture(scope="module")
def find() -> Find:
    emu = power_on(1)  # no game loop under the calls: a battle state can sit in a wait they would break into
    emu.load_adbg(str(IPS) + ".adbg")
    name_find = emu.lookup_symbol_addr("name_find")
    assert name_find is not None

    def run(name_id: int) -> tuple[int, int, int]:
        """name_find with the id at $20 (D = 0): (A, X, Y), Y = MISS when the carry comes back clear."""
        code = bytes([0xC2, 0x30, 0xA9, 0x00, 0x00, 0x5B])  # rep #$30 / lda #0 / tcd
        code += bytes([0xA9]) + name_id.to_bytes(2, "little") + bytes([0x85, 0x20])  # lda #id / sta $20
        code += bytes([0xA2]) + KEPT_X.to_bytes(2, "little")  # ldx #KEPT_X
        code += bytes([0x22]) + name_find.to_bytes(3, "little")  # jsl name_find
        code += bytes([0xB0, 0x03, 0xA0, 0xFF, 0xFF])  # bcs +3 / ldy #MISS
        emu.step()  # finish the instruction the game is paused in: it would complete against the stub's PC
        state = emu.run_asm(code)
        return state.a & 0xFFFF, state.x & 0xFFFF, state.y & 0xFFFF

    return run


def test_every_id_finds_its_entry(find: Find) -> None:
    ids = scan_ids()
    found = {name_id: find(name_id)[2] for name_id in ids}
    assert found == {name_id: 2 * i for i, name_id in enumerate(ids)}


@pytest.mark.parametrize("name_id", [0x0000, 0x0063, 0x0076, 0x1587, 0x273F, 0xFFFF])
def test_an_unknown_id_misses_with_a_zero_like_the_scan(find: Find, name_id: int) -> None:
    assert find(name_id) == (0, KEPT_X, MISS)


def test_x_is_kept_on_a_hit(find: Find) -> None:
    assert find(0x1388)[1] == KEPT_X
