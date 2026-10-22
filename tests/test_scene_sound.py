"""The scene sound ops, played from a field start (tests/warp.py) with the CPU -> APU ports and the SPC700 driver
watched: what each op sends to `$2140-$2143` (port 0 = command | toggle bit 7, ports 1-3 = `$4C-$4E`), what the
driver does with it (its command table at ARAM `$21A2`), and what comes out of the speakers
(notes/text/scene_opcodes.md, Sound).
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING

import pytest
from kintsuki import CB_EXEC

from tests.warp import field, run_script
from tools.scene_asm import assign, imm, op, var

if TYPE_CHECKING:
    from kintsuki import Emu

    from tools.scene_script import Instruction

Command = tuple[int, int, int, int]  # command, p1, p2, p3
CURRENT_SONG, LOADED_SONG = 0x7E00BC, 0x7E00BD
SONGS_HEARD, SFX_HEARD = 0x1E5D, 0x1E0D  # SRAM bit per song / sound effect id: $70:7E5D / 7E0D, 8 KB mirrored
SEQUENCE_STATE = 0x7E0098  # CPU-side sound-sequence player: 0 idle, 1 running, 2 signalled
LEADER_X, LEADER_Y, SCROLL_X = 0x7E2013, 0x7E2016, 0x7E0302
TEMPO = 0xFA  # SPC700 timer 0 target: the driver's tick period
TRACKS = 0x0200  # driver tracks, 0x20 bytes each; +0x18 volume


class Sound:
    """One emulator in the field with the APU traffic, the driver's DSP / timer writes and the audio recorded."""

    def __init__(self, emu: Emu) -> None:
        self.emu = emu
        self.sent: list[Command] = []
        self.tempo: list[int] = []
        self._ports = [0, 0, 0, 0]
        emu.add_write_callback(0x2140, 0x2143, self._port)
        emu.spc_add_write_callback(TEMPO, TEMPO, lambda _a, v: self.tempo.append(v))
        emu.enable_audio(True)

    def _port(self, addr: int, value: int) -> None:
        self._ports[addr & 3] = value
        if addr & 3 == 0:
            self.sent.append((value & 0x7F, self._ports[1], self._ports[2], self._ports[3]))

    def run(self, items: Sequence[str | Instruction], frames: int = 30) -> None:
        self.sent.clear()
        self.tempo.clear()
        self.emu.read_audio()
        run_script(self.emu, items, frames)

    def commands(self, *ids: int) -> list[Command]:
        return [c for c in self.sent if c[0] in ids]

    def loudness(self, frames: int) -> tuple[float, float]:
        """Left and right RMS over the next `frames`."""
        self.emu.read_audio()
        self.emu.run_frames(frames)
        buf = self.emu.read_audio()
        left, right = buf[0::2], buf[1::2]
        return math.sqrt(sum(x * x for x in left) / len(left)), math.sqrt(sum(x * x for x in right) / len(right))

    def heard(self, table: int, sound_id: int) -> int:
        """The SRAM byte holding `sound_id`'s bit, cleared first by `forget`."""
        return int(bytes(self.emu.read_sram())[table + sound_id // 8])

    def forget(self, table: int, sound_id: int) -> None:
        sram = bytearray(self.emu.read_sram())
        sram[table + sound_id // 8] = 0
        self.emu.inject_sram(bytes(sram))

    def aram(self, addr: int, size: int) -> bytes:
        return bytes(self.emu.aram_read(addr, size))


@pytest.fixture(scope="module")
def lab() -> Iterator[tuple[Sound, bytes]]:
    sound = Sound(field("fantasyanime_4"))
    yield sound, bytes(sound.emu.save_state())
    sound.emu.close()


@pytest.fixture
def sound(lab: tuple[Sound, bytes]) -> Sound:
    s, state = lab
    s.emu.load_state(state)
    return s


def _side(left: float, right: float) -> str:
    if max(left, right) < 0.01:
        return "silent"
    if abs(left - right) < 0.01:
        return "centre"
    return "left" if left > right else "right"


def _silence(s: Sound) -> None:
    s.run([op("music_fade_out", 64)], 120)


def test_music_play_uploads_and_starts_the_song(sound: Sound) -> None:
    """7 stop, 5 / 1 / 3 the sequence, 4 / 2 the samples, 6 play."""
    sound.run([op("music_play", 22, 0, 0)], 300)
    assert ([c[0] for c in sound.commands(7, 5, 3, 6)], sound.emu.read(CURRENT_SONG)) == ([7, 5, 3, 6], 22)


def test_music_play_marks_the_song_heard(sound: Sound) -> None:
    sound.forget(SONGS_HEARD, 22)
    sound.run([op("music_play", 22, 0, 0)], 300)
    assert sound.heard(SONGS_HEARD, 22) == 1 << 22 % 8


def test_music_play_of_the_playing_song_sends_nothing(sound: Sound) -> None:
    sound.run([op("music_play", 22, 0, 0)], 300)
    sound.run([op("music_play", 22, 0, 0)], 60)
    assert sound.sent == []


def test_music_play_p2_is_the_aram_page(sound: Sound) -> None:
    """Command 5's p1 = p2: the song data goes to ARAM $3800 + p2 * 256; command 6 plays from there."""
    sound.run([op("music_play", 22, 1, 0)], 300)
    assert [c[:2] for c in sound.commands(5, 6)] == [(5, 1), (6, 1)]


def test_music_play_p3_bit_1_keeps_the_samples(sound: Sound) -> None:
    sound.run([op("music_play", 22, 0, 2)], 300)
    assert (sound.commands(4), len(sound.commands(6))) == ([], 1)


def test_music_play_p3_bit_2_loads_without_playing(sound: Sound) -> None:
    sound.run([op("music_play", 20, 0, 4)], 300)
    sound.loudness(30)  # the old song's tail
    quiet = max(sound.loudness(30))
    assert (sound.commands(6), sound.emu.read(LOADED_SONG), quiet < 0.001) == ([], 20, True)


def test_sound_command_9_starts_the_loaded_song_fading_in(sound: Sound) -> None:
    """9: play the loaded song, p3 the fade-in rate (bigger = faster)."""
    sound.run([op("music_play", 20, 0, 4)], 300)
    state = bytes(sound.emu.save_state())
    sound.run([op("sound_command", 9, 0, 1, 16)], 1)
    sound.emu.run_frames(20)
    slow = max(sound.loudness(30))
    sound.emu.load_state(state)
    sound.run([op("sound_command", 9, 0, 1, 128)], 21)
    fast = max(sound.loudness(30))
    assert (sound.emu.read(CURRENT_SONG), fast > 3 * slow > 0.003) == (20, True)


def test_music_fade_out_rate(sound: Sound) -> None:
    """Command 8, p1 1, p2 = v: bigger v fades faster (100 frames in, v 64 is under a quarter of v 16)."""
    sound.run([op("music_play", 22, 0, 0)], 200)
    state = bytes(sound.emu.save_state())
    levels = []
    for rate in (16, 64):
        sound.emu.load_state(state)
        sound.run([op("music_fade_out", rate)], 100)
        levels.append((sound.commands(8)[0][:3], max(sound.loudness(20))))
    (slow_cmd, slow), (fast_cmd, fast) = levels
    assert (slow_cmd, fast_cmd, fast < slow / 4) == ((8, 1, 16), (8, 1, 64), True)


@pytest.mark.parametrize(("factor", "period"), [(64, 172), (62, 179), (54, 204)])
def test_sound_command_17_sets_the_tempo(sound: Sound, factor: int, period: int) -> None:
    """17: the driver's tempo factor `$90` (0x40 normal, reset by each song start); lower = longer timer period."""
    sound.run([op("music_play", 22, 0, 0)], 120)
    sound.run([op("sound_command", 17, factor, 0, 0)], 10)
    assert sound.tempo == [period]


def test_sound_commands_23_and_24_save_and_restore_the_music(sound: Sound) -> None:
    """23 copies the driver's track state (DP $00-$7F and more) away; 24 puts it back over a reloaded song."""
    snapshots: list[bytes] = []
    hook = sound.emu.spc_add_exec_callback(0x2305, 0x2305, lambda _pc, _v: snapshots.append(sound.aram(0, 0x80)))
    sound.run([op("music_play", 22, 0, 0)], 300)
    sound.run([op("sound_command", 23, 0, 0, 0)], 5)
    saved = sound.aram(0x500, 0x80)
    sound.run([op("music_play", 20, 0, 0)], 300)
    sound.run([op("music_play", 22, 0, 4), op("sound_command", 24, 0, 0, 0)], 200)
    sound.emu.spc_remove_callback(CB_EXEC, hook)
    assert snapshots == [saved]


def test_sound_command_10_fades_the_restored_music_back_in(sound: Sound) -> None:
    """The battle return: reload without playing, 24 restore (silent), then 10 1, 16 fades it in."""
    sound.run([op("music_play", 22, 0, 0)], 300)
    sound.run([op("sound_command", 23, 0, 0, 0), op("music_play", 20, 0, 0)], 300)
    sound.run([op("music_play", 22, 0, 4), op("sound_command", 24, 0, 0, 0)], 260)
    restored = max(sound.loudness(20))
    sound.run([op("sound_command", 10, 1, 16, 0)], 140)
    assert (restored < 0.002, max(sound.loudness(20)) > 0.01) == (True, True)


def test_sound_command_13_sets_track_volume(sound: Sound) -> None:
    """13 hi, lo, v: volume (track +0x18) v on the tracks of the 16-bit mask lo | hi << 8."""
    sound.run([op("music_play", 46, 0, 0)], 300)
    sound.run([op("sound_command", 13, 0x3C, 0xFF, 40)], 3)
    volumes = [sound.aram(TRACKS + t * 0x20 + 0x18, 1)[0] for t in range(16)]
    assert volumes == [40] * 8 + [255, 255, 40, 40, 40, 40, 255, 255]


@pytest.mark.parametrize(("pan", "side"), [(32, "right"), (64, "centre"), (96, "left"), (0, "silent")])
def test_sfx_play_pan(sound: Sound, pan: int, side: str) -> None:
    """Pan 1-127 right to left (L : R = pan : 128 - pan), 64 centre; 0 is silent."""
    _silence(sound)
    sound.run([op("sfx_play", 5, pan)], 1)
    heard = _side(*sound.loudness(40))
    assert heard == side


@pytest.mark.parametrize("screen_x", [8, 128, 240])
def test_sfx_play_pan_ff_follows_the_leader(sound: Sound, screen_x: int) -> None:
    """Pan FF: 0x7F - (leader x - scroll x) / 2, sent as command 12's p3."""
    sound.emu.write_range(LEADER_X, (sound.emu.read16(SCROLL_X) + screen_x).to_bytes(2, "little"))
    sound.run([op("sfx_play", 5, 255)], 10)
    assert sound.commands(12)[0][3] == 0x7F - screen_x // 2


def test_sfx_play_pan_fe_is_random(sound: Sound) -> None:
    sound.run([x for _ in range(6) for x in (op("sfx_play", 5, 254), op("wait", 8))], 80)
    pans = {c[3] for c in sound.commands(12)}
    assert len(pans) > 3 and max(pans) < 0x80


def test_sfx_play_marks_the_sound_heard(sound: Sound) -> None:
    sound.forget(SFX_HEARD, 501)
    sound.run([op("sfx_play", 501, 64)], 10)
    assert sound.heard(SFX_HEARD, 501) == 1 << 501 % 8


@pytest.mark.parametrize(("tiles", "volume"), [(1, 253), (24, 192), (48, 128), (96, 0)])
def test_sound_source_falls_off_with_distance(sound: Sound, tiles: int, volume: int) -> None:
    """Op 1D's point, read by fx channel handler 3 (syscall 17) at C2:F877: volume (0x200 - min(0x200, 2 * (|dx| +
    |dy|) / 3)) / 2, sent as command 0x2E's p2: 768 px away is silent."""
    x, y = sound.emu.read16(LEADER_X) // 8, sound.emu.read16(LEADER_Y) // 8
    start = [assign(var(0, 1), imm(3)), assign(var(2, 1), imm(8)), op("syscall", 17)]
    sound.run([op("sound_source_set", x + tiles, y, 0), *start], 60)
    assert sound.commands(0x2E)[-1][2] == volume


@pytest.mark.parametrize("keep", [False, True])
def test_keep_music_through_battle_keeps_the_music_through_a_battle(sound: Sound, keep: bool) -> None:
    """Syscall 72 (`$02C2` bit 7): the next battle skips the fade-out and its own song (`$0972` = 1)."""
    song = sound.emu.read(CURRENT_SONG)
    sound.run([*([op("syscall", 72)] if keep else []), op("battle_start", 16, 8)], 600)
    kept = (sound.commands(8, 5) == [], sound.emu.read(CURRENT_SONG) == song, sound.emu.read(0x7E0972))
    assert kept == ((True, True, 1) if keep else (False, False, 0))


@pytest.mark.parametrize("signal", [False, True])
def test_sound_signal_releases_the_sequence(sound: Sound, signal: bool) -> None:
    """Sound 519 is a CPU-side sequence that holds at its op 7 until syscall 85 sets `$98` = 2, then fades out."""
    _silence(sound)
    sound.run([op("sfx_play", 519, 64)], 120)
    if signal:
        sound.run([op("syscall", 85)], 2)
    sound.emu.run_frames(240)
    assert (sound.emu.read(SEQUENCE_STATE), max(sound.loudness(30)) > 0.01) == ((0, False) if signal else (1, True))
