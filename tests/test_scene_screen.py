"""Screen effects of the scene VM, played in the patched game from a field save (tests/warp.py): op 1E's kinds, the
fx channels (syscalls 17 / 18, handlers of C2:8ED7), the palette builders (syscalls 6, 41), the letterbox
(syscall 42), the raster wave (syscall 58), the wide OBJ frame (syscall 14), effect presets (syscall 12) and op 2A.

Every test starts from one savestate of the castle field (fantasyanime_3, map 0x1A3), taken once per module.
"""

from __future__ import annotations

import struct
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING

import pytest
from PIL import Image, ImageChops

from tests.screens import assert_matches_golden, picture, tap
from tests.warp import EVENTS, field, run_script, warp
from tools.scene_asm import assemble, assign, op, var

if TYPE_CHECKING:
    from kintsuki import Emu

    from tools.scene_script import Instruction

SAVE = "fantasyanime_3"
CHANNEL_A_BANK = 0x7E0571  # 0 = channel A idle (handlers clear it to stop)
BRIGHTNESS = 0x7E028D  # INIDISP shadow
MOSAIC = 0x7E0294
SFX_PLAY = 0xC0907E  # A = sound effect id, $00 = pan


class Lab:
    """One emulator, its field state, and the sound effects played since the last reset."""

    def __init__(self) -> None:
        self.emu = field(SAVE)
        self.state = self.emu.save_state()
        self.sfx: list[tuple[int, int, int]] = []
        self.emu.add_exec_callback(SFX_PLAY, SFX_PLAY, self._on_sfx)

    def _on_sfx(self, _pc: int, _unused: int) -> None:
        self.sfx.append((self.emu.frame_count, self.emu.get_state().a & 0xFFFF, self.emu.read(0x7E0000)))

    def reset(self) -> Emu:
        self.emu.load_state(self.state)
        self.emu.run_frames(2)
        self.sfx.clear()
        return self.emu


@pytest.fixture(scope="module")
def lab() -> Iterator[Lab]:
    yield Lab()


def syscall(n: int, *args: int) -> list[Instruction]:
    """`syscall n` with var.w[0], var.w[2], ... = args (word stores: a byte store keeps the old high byte)."""
    return [*(assign(var(2 * i, 1), a) for i, a in enumerate(args)), op("syscall", n)]


def changed_pixels(a: Image.Image, b: Image.Image) -> int:
    diff = ImageChops.difference(a, b).convert("L")
    return int(diff.point(lambda v: 255 if v else 0).histogram()[255])


def brightness_after(lab: Lab, items: Sequence[Instruction], frames: int) -> int:
    emu = lab.reset()
    run_script(emu, items, 1)
    emu.run_frames(frames)
    return int(emu.read(BRIGHTNESS) & 0x0F)


# op 1E fade (C2:1EEA)


def test_fade_kind_1_darkens_slowly_at_speed_1(lab: Lab) -> None:
    assert brightness_after(lab, [op("fade", 1, 1)], 24) == 14


@pytest.mark.parametrize("kind", [2, 3])
def test_fade_kind_2_3_alone_change_nothing(lab: Lab, kind: int) -> None:
    assert brightness_after(lab, [op("fade", kind, 1)], 40) == 15


@pytest.mark.parametrize("kind", [2, 3])
def test_fade_kind_2_3_re_rate_a_running_fade(lab: Lab, kind: int) -> None:
    """Kinds 2 / 3 only store the brightness rate ($04A0): a slow fade out finishes at the new, fast rate."""
    assert brightness_after(lab, [op("fade", 1, 1), op("wait", 4), op("fade", kind, 16)], 24) == 0


def test_fade_kind_0_brings_the_screen_back(lab: Lab) -> None:
    assert brightness_after(lab, [op("fade", 1, 16), op("wait", 20), op("fade", 0, 16)], 60) == 15


def test_fade_kind_5_mosaics_out_and_kind_4_back(lab: Lab) -> None:
    """$0294 is MOSAIC: BG1-3 enabled (low bits 7), the size climbing to 16 px, then down again."""
    emu = lab.reset()
    run_script(emu, [op("fade", 5, 2), op("wait", 70), op("fade", 4, 2)], 1)
    trace = []
    for _ in range(140):
        emu.run_frames(1)
        trace.append(emu.read(MOSAIC))
    peak = trace.index(max(trace))
    assert (max(trace), trace[0] & 7, trace[-1] < max(trace), sorted(trace[:peak]) == trace[:peak]) == (
        0xF7,
        7,
        True,
        True,
    )


# syscalls 17 / 18: the fx channels


def channel_a_runs(lab: Lab, items: Sequence[Instruction], frames: int) -> bool:
    emu = lab.reset()
    run_script(emu, items, 1)
    emu.run_frames(frames)
    return bool(emu.read(CHANNEL_A_BANK))


def test_fx_2_circle_script_ends_by_itself(lab: Lab) -> None:
    assert (channel_a_runs(lab, syscall(17, 2, 1), 100), channel_a_runs(lab, syscall(17, 2, 1), 200)) == (True, False)


def test_fx_2_script_3_is_a_green_circle(lab: Lab) -> None:
    emu = lab.reset()
    run_script(emu, syscall(17, 2, 3), 2)
    emu.run_frames(40)
    assert_matches_golden(emu, "screen_fx2_green_circle")


def test_fx_3_plays_an_ambient_sound_loop(lab: Lab) -> None:
    """Handler 3 = sound-effect script (table C2:F42B): script 6 plays effect 500 three times every 70 frames,
    forever."""
    emu = lab.reset()
    run_script(emu, syscall(17, 3, 6), 1)
    start = emu.frame_count
    emu.run_frames(150)
    times = [(f - start, sfx) for f, sfx, _ in lab.sfx]
    assert (times[:6], bool(emu.read(CHANNEL_A_BANK))) == (
        [(0, 500), (10, 500), (20, 500), (70, 500), (80, 500), (90, 500)],
        True,
    )


def lightning(lab: Lab) -> Emu:
    """Scene 11's set-up: CGRAM to $7F:2000 (syscall 65 2), white to $7F:2200 (65 1), then handler 11."""
    emu = lab.reset()
    run_script(
        emu,
        [*syscall(65, 2, 0x2000, 0x200), op("wait", 2), *syscall(65, 1, 0x2200, 0x200), *syscall(17, 11, 6000, 0)],
        6,
    )
    return emu


def test_fx_11_lightning_strikes_with_thunder(lab: Lab) -> None:
    """Random strikes: thunder (effect 11, random pan) and one white frame (the $7F:2220 palette uploaded)."""
    emu = lightning(lab)
    emu.run_frames(120)
    assert len(lab.sfx) >= 3
    assert {sfx for _, sfx, _ in lab.sfx} <= {11, 12}


def test_fx_11_mode_2_restores_and_stops(lab: Lab) -> None:
    emu = lightning(lab)
    emu.run_frames(30)
    run_script(emu, syscall(17, 11, 0, 2), 3)
    assert not emu.read(CHANNEL_A_BANK)


@pytest.mark.parametrize(("channel", "mask"), [(1, 0x7C00), (2, 0x001F), (3, 0x03E0)])
def test_fx_12_tints_then_fades_back(lab: Lab, channel: int, mask: int) -> None:
    """Handler 12: the whole palette with one channel raised (1 blue, 2 red, 3 green), back to $7F:2200 in 32
    frames, then off."""
    emu = lab.reset()
    run_script(emu, [*syscall(65, 2, 0x2000, 0x200), op("wait", 2), *syscall(65, 2, 0x2200, 0x200), op("wait", 2)], 6)
    normal = bytes(emu.cgram_read_range(0, 512))
    plain = struct.unpack("<256H", normal)
    run_script(emu, syscall(17, 12, channel, 0), 4)
    tinted = struct.unpack("<256H", bytes(emu.cgram_read_range(0, 512)))
    raised = sum(1 for a, b in zip(tinted[1:], plain[1:], strict=True) if a & mask > b & mask)
    others = sum(1 for a, b in zip(tinted[1:], plain[1:], strict=True) if a & ~mask & 0x7FFF > b & ~mask & 0x7FFF)
    emu.run_frames(40)
    assert (raised > 100, others, bytes(emu.cgram_read_range(0, 512)) == normal, emu.read(CHANNEL_A_BANK)) == (
        True,
        0,
        True,
        0,
    )


def test_fx_13_cross_fades_bg_palette_1_and_never_stops(lab: Lab) -> None:
    """Handler 13: colours 16-31 step one unit a frame from palette [2] to [4]; the step counter and the stop write
    run with DB = $7F (C2:B306, C2:B315), so the channel stays on and $7F:0591 / $7F:0571 are hit instead."""
    emu = lab.reset()
    before = emu.read(0x7F0591)
    run_script(emu, syscall(17, 13, 15, 28), 1)
    emu.run_frames(100)
    target = bytes(emu.read_range(0x7F2020, 32))
    assert (bytes(emu.cgram_read_range(32, 32)), emu.read(CHANNEL_A_BANK) != 0, emu.read(0x7F0591) != before) == (
        target,
        True,
        True,
    )


@pytest.mark.parametrize(("handler", "colour"), [(7, 0xC0), (8, 0xF0), (9, 0xF0), (10, 0xA0), (13, 0x10)])
def test_fx_cross_fade_targets(lab: Lab, handler: int, colour: int) -> None:
    emu = lab.reset()
    run_script(emu, syscall(17, handler, 15, 28), 2)
    assert emu.read(0x7E058D) == colour


def touch(lab: Lab, first: int, last: int, actor: int, dx: int) -> int:
    """An actor created dx tiles beside the hero, handler 6 watching actors first..last; entry 2/0x7D ($E90D)
    points at a script that marks var.w[0x60]."""
    emu = lab.reset()
    hx, hy = emu.read16(0x7E2013), emu.read16(0x7E2016)
    emu.write_range(0x7EFEC3 + 0x60, bytes(2))
    items: list[str | Instruction] = [
        op("actor_create", actor, 0, hx // 8 + dx, (hy + 16) // 8, 0, 96, 22, 2, 11, 64, 32, 4, 3, 8),
        *syscall(17, 6, first, last),
        op("goto", "idle2"),
        "hit",
        assign(var(0x60, 1), 0x1234),
        op("ret"),
        "idle2",
        op("wait", 1),
        op("goto", "idle2"),
    ]
    start = emu.read16(EVENTS)
    _, labels = assemble([*items, "idle", op("wait", 1), op("goto", "idle")], start, start + 0x40)
    emu.write_range(0x7EE90D, (0x3100 + labels["hit"]).to_bytes(2, "little"))
    run_script(emu, items, 30)
    return int(emu.read16(0x7EFEC3 + 0x60))


@pytest.mark.parametrize(
    ("first", "last", "actor", "dx", "mark"),
    [(16, 16, 16, 0, 0x1234), (16, 24, 18, 0, 0x1234), (16, 16, 16, 4, 0), (17, 20, 16, 0, 0)],
)
def test_fx_6_actor_touching_the_hero_calls_entry_7d(
    lab: Lab, first: int, last: int, actor: int, dx: int, mark: int
) -> None:
    assert touch(lab, first, last, actor, dx) == mark


# syscall 6: the second palette fade set


def test_syscall_6_set_is_rebuilt_when_the_menu_closes(lab: Lab) -> None:
    """$04BC-04C0 are read back by C2:9D07 on the menu's return (C2:6E8D): retargeted behind its back, the buffer
    comes back as the blend to the new palette."""
    emu = lab.reset()
    run_script(emu, syscall(6, 4, 0, 13, 0x6000), 10)
    to_13 = bytes(emu.read_range(0x7F6000, 0x380))
    emu = lab.reset()
    run_script(emu, syscall(6, 4, 0, 27, 0x6000), 10)
    emu.write(0x7E04C0, 13)
    tap(emu, "X")
    emu.run_frames(30)
    tap(emu, "B")
    tap(emu, "B")
    emu.run_frames(120)
    assert bytes(emu.read_range(0x7F6000, 0x380)) == to_13


# syscall 41: a derived palette


def half(c: int) -> int:
    return ((c & 0x1F) >> 1) | ((c & 0x3C0) >> 1) | ((c & 0x7800) >> 1)


@pytest.mark.parametrize("mode", [0, 50, 200, 255, 7])
def test_syscall_41_derives_a_palette(lab: Lab, mode: int) -> None:
    """A = source palette (C6:2378), [2] = RAM palette (0 = $7F:2000), [4] = 0 black, 255 white, 200 doubled
    (saturating), anything else halved; 0xE0 colours."""
    emu = lab.reset()
    source = struct.unpack("<224H", bytes(emu.read_range(0xFD6139, 448)))  # palette 29
    run_script(emu, syscall(41, 29, 0, mode), 2)
    out = struct.unpack("<224H", bytes(emu.read_range(0x7F2000, 448)))

    def double(c: int) -> int:
        return min((c & 0x1F) << 1, 0x1F) | min((c & 0x3E0) << 1, 0x3E0) | min((c & 0x7C00) << 1, 0x7C00)

    want = {0: [0] * 224, 255: [0x7FFF] * 224, 200: [double(c) for c in source]}.get(mode, [half(c) for c in source])
    assert list(out) == want


# syscall 42: letterbox


def bars(emu: Emu) -> int:
    img = picture(emu)
    px = img.load()
    assert px is not None
    return next(y for y in range(img.height) if any(px[x, y] != (0, 0, 0) for x in range(40, 216)))


@pytest.mark.parametrize(("value", "height"), [(8, 0), (10, 8), (16, 32), (20, 48), (28, 80)])
def test_syscall_42_letterbox_height(lab: Lab, value: int, height: int) -> None:
    """Black bands top and bottom of max(0, 4 * A - 32) lines; A = 0 switches the HDMA off."""
    emu = lab.reset()
    run_script(emu, [*syscall(42, value), op("wait", 1)], 3)
    assert bars(emu) == height


def test_syscall_42_zero_removes_it(lab: Lab) -> None:
    emu = lab.reset()
    run_script(emu, [*syscall(42, 20), op("wait", 1), *syscall(42, 0), op("wait", 1)], 4)
    assert (bars(emu), emu.read(0x7E00C7) & 0x26) == (0, 0)


# syscall 58: raster wave


def test_syscall_58_alone_builds_no_table(lab: Lab) -> None:
    """The wave table ($7E:5D00, end $05AC) is built by C2:9F58 during a map load (C6:1157), after the start-up."""
    emu = lab.reset()
    run_script(emu, syscall(58, 1, 40, 512), 4)
    assert (emu.read(0x7E05A9), emu.read16(0x7E05AC)) == (1, 0)


def test_syscall_58_from_a_start_up_waves_bg3(lab: Lab) -> None:
    """Map 123 (scene 27's start-up: 58 16, 5, 256): BG3 H scroll ($2111), amplitude 5 px, 144 lines a period."""
    emu = lab.reset()
    warp(emu, 123, 56, 38, 3)
    emu.run_frames(30)
    entries = (emu.read16(0x7E05AC) - 0x5D00) // 2
    table = struct.unpack(f"<{entries}h", bytes(emu.read_range(0x7E5D00, entries * 2)))
    assert (emu.read(0x7E05A9), emu.read(0x7E02B1), entries, min(table), max(table)) == (16, 0x11, 144, -5, 5)


# syscall 14: wide OBJ frame


def vram_written(lab: Lab, n: int, slot: int) -> list[int]:
    emu = lab.reset()
    emu.vram_write_range(0xC000, bytes([0x5A]) * 0x4000)
    poisoned = bytes(emu.vram_read_range())
    run_script(emu, syscall(n, 46, 0, 0, slot), 2)
    after = bytes(emu.vram_read_range())
    return sorted({i // 2 for i in range(0xE000, 0x10000) if after[i] != poisoned[i]})


def test_syscall_13_loads_16_by_32(lab: Lab) -> None:
    words = vram_written(lab, 13, 1)
    assert (words[0], words[-1], len(words)) == (0x7000, 0x731F, 4 * 0x20)


def test_syscall_14_loads_32_by_32(lab: Lab) -> None:
    """Twice as wide: the slot and the next one's columns (slot 1 at $7000 also fills slot 2's $7020)."""
    words = vram_written(lab, 14, 1)
    assert (words[0], words[-1], len(words)) == (0x7000, 0x733F, 4 * 0x40)


# syscall 12: effect presets


def preset_change(lab: Lab, preset: int) -> int:
    emu = lab.reset()
    run_script(emu, syscall(0), 1)
    emu.run_frames(8)
    calm = picture(emu)
    emu = lab.reset()
    run_script(emu, syscall(12, preset), 1)
    emu.run_frames(8)
    return changed_pixels(picture(emu).crop((96, 88, 176, 168)), calm.crop((96, 88, 176, 168)))


def test_syscall_12_preset_1_explodes_on_the_hero(lab: Lab) -> None:
    assert preset_change(lab, 1) > 300


def test_syscall_12_preset_0_shows_nothing_here(lab: Lab) -> None:
    assert preset_change(lab, 0) == 0


# op 2A camera_pan_axis


def test_camera_pan_axis_moves_one_axis(lab: Lab) -> None:
    """With the x target off the camera, only x moves; with x already there, only y."""
    emu = lab.reset()
    run_script(emu, [op("cutscene_begin"), op("camera_pan_axis", 20, 70, 128)], 2)
    trace = []
    for _ in range(10):
        emu.run_frames(10)
        trace.append((emu.read16(0x7E0302), emu.read16(0x7E0305)))
    assert len({y for _, y in trace}) == 1
    assert len({x for x, _ in trace}) == 10


def test_camera_pan_axis_y_when_x_is_there(lab: Lab) -> None:
    emu = lab.reset()
    x0 = emu.read16(0x7E0302)
    tile_x = x0 // 8 + 14
    run_script(emu, [op("cutscene_begin"), op("camera_pan_axis", tile_x, tile_x, 256)], 2)
    target_y = emu.read16(0x7E0247)
    emu.run_frames(300)
    assert (emu.read16(0x7E0302), emu.read16(0x7E0305)) == (x0, target_y)
