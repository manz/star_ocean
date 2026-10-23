"""Scene ops and syscalls that change game state, played in the patched game (tests/warp.py): tile attributes,
battles, the encounter guard var[0x15], savoir levels, party guests and leavers, the item-find roll, inventory
categories, map flags (notes/text/scene_opcodes.md, scene_syscalls.md).

One emulator for the module: the field of fantasyanime_4 (map 136, hero on cell (25, 14)) and a cave spot of map 123
(cell (40, 40), away from every trigger mark, encounter rate 6) are saved once and loaded back by each test.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.screens import assert_matches_golden, tap
from tests.warp import field, run_script, set_var, walk, warp
from tools.encode_text import fr_table
from tools.scene_asm import op
from tools.scene_script import Value

if TYPE_CHECKING:
    from kintsuki import Emu

    from tools.scene_script import Instruction

HERO_X, HERO_Y = 0x7E2013, 0x7E2016
GRID = 0x7EEE73  # attribute grid, 16 px cells, row width [$0307]
VAR15 = 0x7EFED8
RESULT = 0x7E0278
RECORDS = 0x7E6FE1  # 8 x 0x100, battle party = records 4-7
SAVOIRS = 0x7E84E1  # record k: 0x40 savoir levels at SAVOIRS + k * 0x40
ENEMIES = 0x7E77E2  # battle enemy slot n: id at +0x100 * n
ROLL = 0xC27030  # the random encounter roll, after the var[0x15] == 2 test (C2:7029)
ITEMS, COUNTS = 0x7E7FE1, 0x7E81E1
CB_EXEC = 0
RATIX, IRIA = 0, 4  # character ids - 1: battle party slots 0 and 1 of the save
IRIA_RECORD = RECORDS + 5 * 0x100


@dataclass
class Game:
    emu: Emu
    field: bytes
    cave: bytes

    def at(self, state: bytes) -> Emu:
        self.emu.load_state(state)
        return self.emu


@pytest.fixture(scope="module")
def game() -> Iterator[Game]:
    emu = field("fantasyanime_4")
    start = emu.save_state()
    warp(emu, 123, 80, 80, 2)
    emu.run_frames(60)
    yield Game(emu, start, emu.save_state())
    emu.close()


def _pace(emu: Emu, pc: int, steps: int) -> int:
    """Times `pc` runs while the hero walks left and right `steps` times."""
    hits = [0]
    cb = emu.add_exec_callback(pc, pc, lambda _a, _v: hits.__setitem__(0, hits[0] + 1))
    try:
        for i in range(steps):
            walk(emu, ["LEFT", "RIGHT"][i % 2], 40)
    finally:
        emu.remove_callback(CB_EXEC, cb)
    return hits[0]


def _script(emu: Emu, items: list[str | Instruction], frames: int = 30) -> int:
    run_script(emu, items, frames)
    result: int = emu.read16(RESULT)
    return result


def _inventory(emu: Emu) -> dict[int, int]:
    ids, counts = bytes(emu.read_range(ITEMS, 512)), bytes(emu.read_range(COUNTS, 512))
    return {ids[i] | (counts[i] >> 7) << 8: counts[i] & 0x3F for i in range(512) if ids[i] or counts[i] & 0x80}


# ops 3A / 3B: the attribute's bit 6 is a wall


@pytest.mark.parametrize(("attr", "x"), [(0, 368), (64, 400)])
def test_tile_attr_64_is_a_wall(game: Game, attr: int, x: int) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("tile_attr_set", 24, 14, attr)])  # the cell left of the hero
    walk(emu, "LEFT", 40)
    assert emu.read16(HERO_X) == x


def test_tile_attr_fill_0_opens_a_wall(game: Game) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("tile_attr_fill", 29, 13, 29, 15, 0)])  # the map's own wall, 64 at x 29
    walk(emu, "RIGHT", 80)
    assert emu.read16(HERO_X) == 496  # past it; 448 (cell 28) without the fill


# op 15: formation, battlefield


@pytest.mark.parametrize(("formation", "enemies"), [(13, [1, 1, 0]), (37, [36, 4, 13])])
def test_battle_start_formation_picks_the_enemies(game: Game, formation: int, enemies: list[int]) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("battle_start", formation, 0)])
    emu.run_frames(120)
    assert [emu.read(ENEMIES + n * 0x100) for n in range(3)] == enemies


def test_battle_start_param_is_the_battlefield(game: Game) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("battle_start", 13, 2)])
    emu.run_frames(200)
    assert_matches_golden(emu, "state_battlefield_2")  # the river backdrop, not map 136's own


def test_a_random_encounter_takes_the_maps_battlefield(game: Game) -> None:
    emu = game.at(game.cave)
    emu.write(VAR15, 0)
    for i in range(150):
        walk(emu, ["LEFT", "RIGHT"][i % 2], 40)
        if emu.read(0x7E02C2) & 2:
            break
    assert (emu.read(0x7E0B8C), emu.read(0x7E028C)) == (12, 12)  # scene 27's battle_start 37, 12 in this cave


# syscall 83 / var[0x15]: 2 turns random encounters off


@pytest.mark.parametrize(("value", "rolls"), [(0, True), (2, False)])
def test_var15_2_skips_the_encounter_roll(game: Game, value: int, rolls: bool) -> None:
    emu = game.at(game.cave)
    emu.write(VAR15, value)
    assert (_pace(emu, ROLL, 20) > 0) is rolls


@pytest.mark.parametrize(("before", "after"), [(1, 0), (2, 2)])
def test_syscall_83_keeps_a_2(game: Game, before: int, after: int) -> None:
    emu = game.at(game.field)
    emu.write(VAR15, before)
    set_var(emu, 0, 0)
    run_script(emu, [op("syscall", 83)])
    assert emu.read(VAR15) == after


# ops 66 / 67: savoir levels


def test_char_table_is_the_savoir_level(game: Game) -> None:
    emu = game.at(game.field)
    level = _script(emu, [op("char_table_set", RATIX, 0, 3), op("char_table_get", RATIX, 0), op("store_result", 8)])
    assert (level, emu.read(SAVOIRS + 4 * 0x40)) == (3, 3)  # Ratix is record 4: battle party slot 0


def test_the_savoirs_menu_shows_it(game: Game) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("char_table_set", RATIX, 0, 3), op("char_table_set", RATIX, 11, 4)])
    tap(emu, "X,DOWN,RIGHT,A,A")
    emu.run_frames(30)
    assert_matches_golden(emu, "state_savoirs")  # Biologie 3, Efficacité 4


def test_the_scripts_offsets_land_past_the_rows(game: Game) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("char_table_set", RATIX, Value("imm", 0x7E012C, 2), 5)])  # scene 50's operand
    assert emu.read(SAVOIRS + 4 * 0x40 + 0x12C) == 5


# syscall 84: the party's best Oracle (specialty 0x0A: rounded mean of savoirs 0x0E, 0x05, 0x0C, 0 if one is 0)


@pytest.mark.parametrize(("levels", "oracle"), [((10, 10, 10), 10), ((4, 5, 6), 5), ((10, 0, 10), 0)])
def test_syscall_84_is_the_best_oracle(game: Game, levels: tuple[int, int, int], oracle: int) -> None:
    emu = game.at(game.field)
    for k in range(8):
        for savoir in (0x0E, 0x05, 0x0C):
            emu.write(SAVOIRS + k * 0x40 + savoir, 0)
    for savoir, level in zip((0x0E, 0x05, 0x0C), levels, strict=True):
        emu.write(SAVOIRS + 4 * 0x40 + savoir, level)
    tap(emu, "X,B")  # closing the menu recomputes the party values (CA:CA4E)
    emu.run_frames(60)
    assert _script(emu, [op("syscall", 84), op("store_result", 8)]) == oracle


# syscalls 43 / 44: guest; op 47: leave


def test_syscall_43_makes_a_guest(game: Game) -> None:
    emu = game.at(game.field)
    set_var(emu, 0, IRIA)
    pos = _script(emu, [op("syscall", 43), op("char_party_pos", IRIA), op("store_result", 8)])
    assert (emu.read(IRIA_RECORD + 1), pos) == (0x45, 0)


def test_a_guest_shows_as_pnj(game: Game) -> None:
    emu = game.at(game.field)
    set_var(emu, 0, IRIA)
    run_script(emu, [op("syscall", 43)])
    tap(emu, "X")
    emu.run_frames(20)
    assert_matches_golden(emu, "state_guest")  # Iria: PNJ for her level, no HP / MP


def test_syscall_44_ends_the_guest(game: Game) -> None:
    emu = game.at(game.field)
    set_var(emu, 0, IRIA)
    pos = _script(emu, [op("syscall", 43), op("syscall", 44), op("char_party_pos", IRIA), op("store_result", 8)])
    assert (emu.read(IRIA_RECORD + 1), pos) == (5, 2)


def test_party_leave_moves_the_record_out(game: Game) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("party_leave", IRIA)])
    ids = [emu.read(RECORDS + 1 + k * 0x100) for k in range(8)]
    assert ids == [2, 4, 11, 0x85, 1, 12, 8, 7]  # bit 7, before the battle party; reserve 7 moves in


def test_party_leave_returns_two_equipment_slots(game: Game) -> None:
    emu = game.at(game.field)
    before = _inventory(emu)
    run_script(emu, [op("party_leave", IRIA)])
    after = _inventory(emu)
    gained = {i: n for i, n in after.items() if n != before.get(i)}
    assert gained == {0xBD: 1, 0x1FF: 1}  # her +0xA8 / +0xA6; +0x9C-0xA4 stay on her


# syscall 55: an item-find roll


def test_syscall_55_finds_an_item(game: Game) -> None:
    emu = game.at(game.cave)
    emu.write(0x7E0473, emu.read(0x7E0473) | 0x10)  # the map flag the scenes that call it have
    before = _inventory(emu)
    for _ in range(20):  # 25% each
        run_script(emu, [op("syscall", 55), op("cutscene_end")], 2)
        if emu.read(0x7E05A4):
            break
    emu.run_frames(240)
    tap(emu, "A")
    emu.run_frames(120)
    after = _inventory(emu)
    assert sum(after.values()) == sum(before.values()) + 1


FOUND = fr_table().to_bytes(" a été obtenu !") + b"\x01\xff\xff"  # chest_found: page wait, end


def test_syscall_55_message_is_french(game: Game) -> None:
    """C6:DD40 builds the message at $7E:6100 like a chest: src/dialog/chest.s gives it the French suffix."""
    emu = game.at(game.cave)
    emu.write(0x7E0473, emu.read(0x7E0473) | 0x10)
    for _ in range(20):
        run_script(emu, [op("syscall", 55), op("cutscene_end")], 2)
        if emu.read(0x7E05A4):
            break
    emu.run_frames(120)
    suffix = bytes(emu.read_range(0x7E6108, len(FOUND)))  # after colour, item, colour
    assert suffix == FOUND
    assert_matches_golden(emu, "state_item_find")  # "Collier a été obtenu !"


# syscalls 70 / 77: categories 1 / 2 split the inventory


@pytest.mark.parametrize(("syscall", "left"), [(70, 83), (77, 2)])
def test_inventory_categories_split(game: Game, syscall: int, left: int) -> None:
    emu = game.at(game.field)
    run_script(emu, [op("syscall", syscall)])
    assert len(_inventory(emu)) == left  # of 85: 70 drops the two category 1 items, 77 keeps only them


# syscalls 66 / 67: $0439 bit 0x10 runs the map's palette animation


@pytest.mark.parametrize(("syscall", "animated"), [(66, True), (67, False)])
def test_map_flag_0x10_animates_the_palette(game: Game, syscall: int, animated: bool) -> None:
    emu = game.at(game.field)
    set_var(emu, 0, 0x10)
    run_script(emu, [op("syscall", syscall)], 2)
    seen = set()
    for _ in range(40):
        emu.run_frames(6)
        seen.add(bytes(emu.cgram_read_range(0, 512)))
    assert (len(seen) > 1) is animated


# syscall 71


@pytest.mark.parametrize(("pre", "bit"), [([op("syscall", 71)], 0x20), ([], 0)])
def test_syscall_71_bit_survives_battle_start(game: Game, pre: list[str | Instruction], bit: int) -> None:
    emu = game.at(game.field)
    run_script(emu, [*pre, op("battle_start", 13, 0)])
    assert emu.read(0x7E02C2) & 0x20 == bit
