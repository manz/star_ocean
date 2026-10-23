"""What the actor operands do in the running game (notes/text/scene_opcodes.md, Actors): an actor is created next to
the hero by an injected script (tests/warp.py), one operand varied at a time, and the effect read back from the actor
record, the OAM the game builds from it, or the picture.

Save fantasyanime_1 stands the hero alone on map 41 at tile (40, 138), facing down; fantasyanime_3 in the castle
courtyard (map 419), where wandering actors have room to walk. One emulator serves the module: each test starts from a
snapshot of its save.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from PIL import Image

from tests.screens import GOLDENS, STATES, picture, tap
from tests.warp import EVENTS, LOADED, SAVES, VARS, field, run_script, walk
from tools.scene_asm import assemble, assign, op, var

if TYPE_CHECKING:
    from kintsuki import Emu

    from tools.scene_script import Instruction

ACTOR = 0x7E2000
HERO_X, HERO_Y = 40, 138  # fantasyanime_1, tiles
# actor_create operands after n: mode, x, y, facing, sheet, +09, +2F, +01, +30, height, +0F, +04, +02
CREATE = {
    "mode": 0,
    "x": HERO_X + 4,
    "y": HERO_Y,
    "facing": 2,
    "sheet": 6,
    "motion": 3,
    "speed": 2,
    "flags": 0x19,
    "depth": 0x40,
    "height": 32,
    "priority": 4,
    "size": 2,
    "flags2": 0,
}
TALKED = 0x7E  # a variable map 41's scene leaves alone


@pytest.fixture(scope="module")
def saves() -> Iterator[tuple[Emu, dict[int, bytes]]]:
    emu = field("fantasyanime_1")
    states = {1: emu.save_state()}
    emu.load_state((STATES / "load_screen.kss").read_bytes())  # the same emulator: one per process
    emu.inject_sram((SAVES / "fantasyanime_3.srm").read_bytes()[:0x2000])
    emu.run_frames(1)
    tap(emu, "A,A")
    emu.run_frames(LOADED)
    states[3] = emu.save_state()
    yield emu, states


def _at(saves: tuple[Emu, dict[int, bytes]], save: int = 1) -> Emu:
    emu, states = saves
    emu.load_state(states[save])
    emu.run_frames(1)
    return emu


def _create(n: int = 1, **operands: int) -> Instruction:
    args = {**CREATE, **operands}
    return op("actor_create", n, *args.values())


def _field(emu: Emu, n: int, offset: int, size: int = 1) -> int:
    return int.from_bytes(bytes(emu.read_range(ACTOR + n * 0x40 + offset, size)), "little")


def _oam(emu: Emu, x: int) -> list[tuple[int, int, int, int]]:
    """(index, y, tile, attribute) of the on-screen OAM entries at screen x."""
    oam = bytes(emu.oam_read_range())
    out = []
    for k in range(128):
        ox, oy, tile, attr = oam[k * 4 : k * 4 + 4]
        ox |= (oam[512 + k // 4] >> (k % 4 * 2) & 1) << 8
        if ox == x and oy < 224:
            out.append((k, oy, tile | (attr & 1) << 8, attr))
    return out


ACTOR_SX, HERO_SX = 152, 120  # screen x of the created actor's sprite (tile x 44) and the hero's


# +0x30: the sort key of the sprite object list (C3:8BB7), lower first in OAM, so drawn over the others


@pytest.mark.parametrize(
    ("depth", "y", "over"),
    [(0x20, HERO_Y, True), (0x40, HERO_Y, True), (0x64, HERO_Y, False), (0x64, HERO_Y + 2, False)],
)
def test_depth_orders_the_sprites(saves: tuple[Emu, dict[int, bytes]], depth: int, y: int, over: bool) -> None:
    """Overlapping the hero (+0x30 = 0x40): a lower depth draws over him, a tie too (inserted first), a higher one
    under him, even standing in front (y is not a sort key)."""
    emu = _at(saves)
    run_script(emu, [_create(x=HERO_X + 1, y=y, depth=depth)], 30)
    actor, hero = _oam(emu, HERO_SX + 8)[0][0], _oam(emu, HERO_SX)[0][0]
    assert (actor < hero) == over


# +0x0F bits 0-1: the OBJ priority against the BG layers; 4 takes the map's ($043A)


@pytest.mark.parametrize("priority", [0, 1, 2, 3])
def test_priority_is_the_oam_priority(saves: tuple[Emu, dict[int, bytes]], priority: int) -> None:
    emu = _at(saves)
    run_script(emu, [_create(priority=priority)], 30)
    assert {attr >> 4 & 3 for _, _, _, attr in _oam(emu, ACTOR_SX)} == {priority}


def test_priority_4_takes_the_map_default(saves: tuple[Emu, dict[int, bytes]]) -> None:
    emu = _at(saves)
    run_script(emu, [_create(priority=4)], 30)
    assert _field(emu, 1, 0x0F) & 3 == emu.read(0x7E043A) & 3


# +0x02 bit 2: OBJ palettes 4-7 (the ones colour math applies to); bit 4 keeps it as given, else the map's $0438


@pytest.mark.parametrize(("flags2", "palette"), [(0x10, 0), (0x14, 4), (0x00, 4)])
def test_flags2_bit2_picks_the_upper_palettes(saves: tuple[Emu, dict[int, bytes]], flags2: int, palette: int) -> None:
    """Map 41 has $0438 = 1, which sets the bit unless bit 4 is given."""
    emu = _at(saves)
    run_script(emu, [_create(flags2=flags2)], 30)
    assert {attr >> 1 & 7 for _, _, _, attr in _oam(emu, ACTOR_SX)} == {palette}


# +0x04: size class, the width of the off-screen test (C6:42A4: 8, 16, 16, 32, 96 px) and the shadow


@pytest.mark.parametrize(("size", "on_screen"), [(0, False), (1, False), (2, False), (3, True), (4, True)])
def test_size_widens_the_on_screen_test(saves: tuple[Emu, dict[int, bytes]], size: int, on_screen: bool) -> None:
    """24 px left of the camera: only a 32 px or wider actor still counts as on screen (+0x00 bit 3)."""
    emu = _at(saves)
    left = emu.read16(0x7E0302)
    run_script(emu, [_create(x=(left - 24) // 8, size=size)], 10)
    assert bool(_field(emu, 1, 0) & 8) == on_screen


@pytest.mark.parametrize(
    ("height", "size", "shadow"),
    [(16, 2, [(104, 0xC4)]), (32, 2, [(120, 0xC4)]), (48, 2, [(136, 0xC4)]), (32, 3, [(120, 0xC6), (120, 0xCA)])],
)
def test_shadow_sits_at_height(
    saves: tuple[Emu, dict[int, bytes]], height: int, size: int, shadow: list[tuple[int, int]]
) -> None:
    """+0x01 bit 4 (cleared by actor_create, set here with op 5E) draws a shadow height - 16 px below the sprite's
    top, whose body stays put; size 3 has a 32 px wide shadow."""
    emu = _at(saves)
    run_script(emu, [_create(height=height, size=size), op("actor_field_or", 1, 1, 0x10)], 10)
    body = [y for _, y, t, _ in _oam(emu, ACTOR_SX) if t < 0xC0]  # its VRAM tiles vary
    shadows = sorted(
        (y, t) for sx in (ACTOR_SX - 8, ACTOR_SX, ACTOR_SX + 8) for _, y, t, _ in _oam(emu, sx) if t >= 0xC0
    )
    assert (body, shadows) == ([104, 120], shadow)


# +0x01: bit 0 the actor walks through the others, bit 1 the others walk through it, bit 3 it moves off screen


@pytest.mark.parametrize(("flags", "x"), [(0x18, 336), (0x19, 320)])
def test_flags_bit0_walks_through(saves: tuple[Emu, dict[int, bytes]], flags: int, x: int) -> None:
    """Walking 4 tiles left onto the hero (x 320): stopped 16 px short, or on through him."""
    emu = _at(saves)
    run_script(emu, [_create(flags=flags), op("actor_walk", 1, 3, 4, 2)], 150)
    assert _field(emu, 1, 0x13, 2) == x


@pytest.mark.parametrize(("flags", "past"), [(0x09, False), (0x0B, True)])
def test_flags_bit1_lets_the_hero_through(saves: tuple[Emu, dict[int, bytes]], flags: int, past: bool) -> None:
    """The hero walking right at an actor 3 tiles away (x 344) stops at 328, or walks on past it."""
    emu = _at(saves)
    run_script(emu, [_create(x=HERO_X + 3, flags=flags)], 2)
    walk(emu, "RIGHT", 40)
    assert (emu.read16(ACTOR + 0x13) > (HERO_X + 3) * 8) == past


@pytest.mark.parametrize(("flags", "moved"), [(0x01, False), (0x09, True)])
def test_flags_bit3_moves_off_screen(saves: tuple[Emu, dict[int, bytes]], flags: int, moved: bool) -> None:
    emu = _at(saves)
    run_script(emu, [_create(x=HERO_X + 40, flags=flags), op("actor_walk", 1, 3, 2, 2)], 60)
    assert (_field(emu, 1, 0x13, 2) != (HERO_X + 40) * 8) == moved


# +0x02 bit 5: a walk to a target off both axes goes vertically first


@pytest.mark.parametrize(("flags2", "first"), [(0x00, "x"), (0x20, "y")])
def test_flags2_bit5_walks_vertically_first(saves: tuple[Emu, dict[int, bytes]], flags2: int, first: str) -> None:
    emu = _at(saves)
    start = (HERO_X + 4) * 8, HERO_Y * 8 - 16
    run_script(emu, [_create(flags2=flags2), op("actor_walk_to", 1, HERO_X + 8, HERO_Y + 4, 2)], 10)
    x, y = _field(emu, 1, 0x13, 2), _field(emu, 1, 0x16, 2)
    assert {"x": (x != start[0], y == start[1]), "y": (x == start[0], y != start[1])}[first] == (True, True)


# A pressed facing actor n calls the scene's kind 0 entry n; +0x02 bit 3 makes the actor deaf to it


def _talk(emu: Emu, flags2: int) -> int:
    items: list[str | Instruction] = [
        op("goto", "main"),
        "talk",
        assign(var(TALKED, 1), 1),
        op("end"),
        "main",
        _create(x=HERO_X + 2, flags2=flags2),
        op("actor_face_right", 0),
    ]
    base = emu.read16(EVENTS)
    _, labels = assemble([*items, "idle", op("wait", 1), op("goto", "idle")], base, base + 0x40)
    run_script(emu, items, 10)
    emu.write_range(0x7EE615, (0x3100 + labels["talk"]).to_bytes(2, "little"))  # kind 0, id 1
    emu.write_range(VARS + TALKED, b"\0\0")
    tap(emu, "A")
    return int(emu.read16(VARS + TALKED))


@pytest.mark.parametrize(("flags2", "talked"), [(0x00, 1), (0x08, 0)])
def test_a_facing_an_actor_calls_its_entry(saves: tuple[Emu, dict[int, bytes]], flags2: int, talked: int) -> None:
    assert _talk(_at(saves), flags2) == talked


# op 08 npc_create: +0x09 motion kind (C6:2E14), +0x2F its speed (C2:19F9: 0, 1/4, 1/2, 1, 2, 4 px a frame)


def _trail(emu: Emu, kind: int, speed: int, frames: int) -> set[tuple[int, int]]:
    """npc_create 1 in the courtyard: the per-frame velocities (+0x1A, +0x1C, 8.8) seen over `frames`."""
    run_script(emu, [op("npc_create", 1, 17, 20, 2, 6, kind, speed)], 1)
    seen = set()
    for _ in range(frames):
        emu.run_frames(1)
        seen.add((_field(emu, 1, 0x1A, 2), _field(emu, 1, 0x1C, 2)))
    return seen


@pytest.mark.parametrize(("speed", "step"), [(1, 0x40), (2, 0x80), (3, 0x100), (4, 0x200)])
def test_wander_speed_is_the_motion_param(saves: tuple[Emu, dict[int, bytes]], speed: int, step: int) -> None:
    """Kind 1 wanders: random direction, then a pause, at the speed the param picks."""
    seen = _trail(_at(saves, 3), 1, speed, 120)
    assert {abs(v - 0x10000 if v & 0x8000 else v) for pair in seen for v in pair} == {0, step}


@pytest.mark.parametrize("kind", [0, 2, 3])
def test_standing_kinds_stay(saves: tuple[Emu, dict[int, bytes]], kind: int) -> None:
    assert _trail(_at(saves, 3), kind, 2, 240) == {(0, 0)}


# op 12 actor_set_anim: entries of the sheet's animation list (C6:56DE); 0 is the facing's own


def _look(emu: Emu, steps: list[Instruction]) -> list[str]:
    run_script(emu, [_create(flags=0x09), *steps], 2)
    out = []
    for _ in range(6):
        emu.run_frames(8)
        out.append(hashlib.md5(picture(emu).crop((144, 88, 176, 136)).tobytes()).hexdigest())
    return out


FACE = ("actor_face_up", "actor_face_right", "actor_face_down", "actor_face_left")


@pytest.mark.parametrize("facing", [0, 1, 2, 3])
def test_anims_4_to_7_stand_facing(saves: tuple[Emu, dict[int, bytes]], facing: int) -> None:
    standing = _look(_at(saves), [op(FACE[facing], 1)])
    assert _look(_at(saves), [op("actor_set_anim", 1, 4 + facing)]) == standing


@pytest.mark.parametrize(("anim", "cycles"), [(1, True), (2, True), (3, True), (6, False), (8, True), (10, True)])
def test_anims_1_to_3_and_8_to_11_cycle(saves: tuple[Emu, dict[int, bytes]], anim: int, cycles: bool) -> None:
    """1-3 walk (right, down, left; 0 is taken by the default), 8-11 run: +0x29, the frame, moves on."""
    emu = _at(saves)
    run_script(emu, [_create(), op("actor_set_anim", 1, anim)], 2)
    frames = set()
    for _ in range(40):
        emu.run_frames(2)
        frames.add(_field(emu, 1, 0x29))
    assert (len(frames) > 1) == cycles


# Syscalls 1-4, 23, 24: +0x2C is the sprite's width in 16ths, +0x2D its vertical step (8.8, 0x100 = 1:1)


def _strip(emu: Emu, steps: list[Instruction], frames: int = 2, count: int = 12) -> Image.Image:
    run_script(emu, [_create(), *steps], 1)
    strip = Image.new("RGB", (48 * count, 64))
    for k in range(count):
        strip.paste(picture(emu).crop((136, 72, 184, 136)), (48 * k, 0))
        emu.run_frames(frames)
    return strip


def _call(n: int, *args: int) -> list[Instruction]:
    return [assign(var(0, 1), 1), *(assign(var(2 + 2 * i, 1), a) for i, a in enumerate(args)), op("syscall", n)]


@pytest.mark.parametrize("n", [1, 2, 3, 4, 23, 24])
def test_vanish_and_appear_pictures(saves: tuple[Emu, dict[int, bytes]], n: int) -> None:
    """1 / 3 squeeze to a tall thin line and go, 2 / 4 the reverse; 23 narrows only (+0x2D stays 0x100); 24 squashes
    into the ground (+0x2D doubles)."""
    emu = _at(saves)
    strip = _strip(emu, _call(n))
    _assert_strip(strip, f"actors_syscall{n}")


def _assert_strip(strip: Image.Image, name: str) -> None:
    golden = GOLDENS / f"{name}.png"
    if not golden.exists():
        strip.save(golden)
        pytest.skip(f"recorded {golden.name}")
    assert Image.open(golden).convert("RGB").tobytes() == strip.tobytes()


@pytest.mark.parametrize(("n", "priority", "end"), [(1, 3, 0), (3, 2, 0), (2, 2, 0x80), (4, 2, 0x80), (23, 2, 0)])
def test_vanish_and_appear_end(saves: tuple[Emu, dict[int, bytes]], n: int, priority: int, end: int) -> None:
    """1 and 2 raise the priority to 3 meanwhile (2 puts it back), 3 / 4 / 23 keep it; vanishing turns the actor off."""
    emu = _at(saves)
    run_script(emu, [_create(), *_call(n)], 8)
    during = _field(emu, 1, 0x0F) & 3
    emu.run_frames(40)
    assert (during, _field(emu, 1, 0) & 0x80) == ({1: 3, 2: 3}.get(n, priority), end)


# Syscall 21: [2] x speed (8.8), [4] height factor, [6] pause between hops (0 one hop, 0xFFFF hop and go)


@pytest.mark.parametrize(("speed", "factor", "peak", "dx"), [(128, 3, 27, 16), (0, 1, 9, 0), (0xFF80, 2, 18, -16)])
def test_jump_arc(saves: tuple[Emu, dict[int, bytes]], speed: int, factor: int, peak: int, dx: int) -> None:
    """A 32-frame hop, 9 px high per unit of [4], [2] / 256 px a frame across."""
    emu = _at(saves)
    run_script(emu, [_create(), *_call(21, speed, factor, 0)], 1)
    ys = []
    for _ in range(40):
        emu.run_frames(1)
        ys.append(_field(emu, 1, 0x16, 2))
    assert (ys[-1] - min(ys), _field(emu, 1, 0x13, 2) - (HERO_X + 4) * 8) == (peak, dx)


@pytest.mark.parametrize(("pause", "hops"), [(0, 1), (20, 3), (60, 2)])
def test_jump_pause_repeats(saves: tuple[Emu, dict[int, bytes]], pause: int, hops: int) -> None:
    emu = _at(saves)
    run_script(emu, [_create(), *_call(21, 0, 1, pause)], 1)
    ground, count, up = (HERO_Y * 8 - 16), 0, False
    for _ in range(150):  # a hop lasts 32 frames, then the pause and a few more
        emu.run_frames(1)
        air = _field(emu, 1, 0x16, 2) != ground
        count += air and not up
        up = air
    assert count == hops


def test_jump_ffff_hops_away(saves: tuple[Emu, dict[int, bytes]]) -> None:
    emu = _at(saves)
    run_script(emu, [_create(), *_call(21, 128, 3, 0xFFFF)], 40)
    assert (_field(emu, 1, 0) & 0x80, _field(emu, 1, 0x16, 2) < HERO_Y * 8 - 16) == (0, True)


# Syscalls 50-52: $0460, the OBJ priority (0 / 2 / 3) of an actor attached to another by motion kind 15


@pytest.mark.parametrize(("n", "priority"), [(50, 0), (51, 2), (52, 3)])
def test_spawn_attr_is_the_attached_priority(saves: tuple[Emu, dict[int, bytes]], n: int, priority: int) -> None:
    emu = _at(saves)
    run_script(
        emu, [op("syscall", n), _create(), _create(2), op("actor_set", 2, 0x10, 1), op("actor_set", 2, 9, 15)], 10
    )
    assert (_field(emu, 2, 0x0F) & 3, _field(emu, 2, 0x30)) == (priority, 0x50)


# actor_create's mode operand is +0x07: the actor starts in that scripted mode


def test_create_mode_starts_a_scripted_mode(saves: tuple[Emu, dict[int, bytes]]) -> None:
    emu = _at(saves)
    run_script(emu, [_create(mode=2)], 1)
    mode, widths = _field(emu, 1, 7), []
    for _ in range(12):
        emu.run_frames(1)
        widths.append(_field(emu, 1, 0x2C))
    assert (mode, widths == sorted(widths), widths[0] < widths[-1]) == (2, True, True)  # growing, as syscall 2
