"""Count the battle's late steps in kintsuki: the patched game (build/star_ocean.sfc + its IPS) runs a battle state
for 600 frames, A tapped every 10, and the frames where the sprites move (OAM's position table changes) are
counted. At full speed they move every 2 frames; a gap of 3 or 4 is a late step, a gap of 1 catches up. Gaps of 7
and more are the victory slow motion (logic one pass in 4) or a still screen, not slowdown.

    uv run python -m tools.battle_bench               # both states
    uv run python -m tools.battle_bench --profile     # and where the time goes on frames under 15% idle

States: tests/states/battle_chest.kss (early fight, chest animation), battle_busy.kss (late party, spells; its item
menu is closed first). Each runs in its own process: kintsuki allows one emulator per process.
"""

from __future__ import annotations

import itertools
import subprocess
import sys
from collections import Counter

from tools.rom import ROOT

STATES = ("battle_chest", "battle_busy")
FRAMES = 600
OAM_POSITIONS = 512  # OAM's low table; the 32-byte high table also changes on its own
WAITS = (0xC08496, 0xC084AB)  # vblank and NMI-flag waits: idle time
FRAME_CYCLES = 357366  # master cycles per NTSC frame


def bench(state: str, profile: bool) -> str:
    from kintsuki import Button, Emu

    emu = Emu(load_srm_sidecar=False, sram_policy="fit")
    emu.load_rom(str(ROOT / "build" / "star_ocean.sfc"))
    emu.load_state((ROOT / "tests" / "states" / f"{state}.kss").read_bytes())
    emu.run_frames(1)
    if state == "battle_busy":
        for _ in range(3):
            emu.press(0, Button.B, True)
            emu.run_frames(4)
            emu.press(0, Button.B, False)
            emu.run_frames(30)
    moves: list[int] = []
    oam = b""
    excl: Counter[int] = Counter()
    incl: Counter[int] = Counter()
    heavy = 0
    for frame in range(FRAMES):
        emu.press(0, Button.A, frame % 10 < 3)
        if profile:
            emu.profile_start()
        emu.run_frames(1)
        positions = bytes(emu.oam_read_range())[:OAM_POSITIONS]
        if positions != oam:
            moves.append(frame)
            oam = positions
        if not profile:
            continue
        stats = emu.profile_stop()
        if sum(s.excl_cycles for s in stats if s.pc in WAITS) < 0.15 * FRAME_CYCLES:
            heavy += 1
            for s in stats:
                excl[s.pc] += s.excl_cycles
                incl[s.pc] += s.incl_cycles
    gaps = Counter(b - a for a, b in itertools.pairwise(moves))
    late = gaps[3] + gaps[4]
    slow = sum(n for gap, n in gaps.items() if gap >= 7)
    lines = [f"{state}: {len(moves)} steps, {late} late, {gaps[1]} caught up, {slow} slow-motion or still"]
    if heavy:
        scale = 100 / (heavy * FRAME_CYCLES)
        lines.append(f"  {heavy} frames under 15% idle")
        lines.append("  self:  " + ", ".join(f"{pc:06X} {v * scale:.0f}%" for pc, v in excl.most_common(10)))
        lines.append("  total: " + ", ".join(f"{pc:06X} {v * scale:.0f}%" for pc, v in incl.most_common(14)))
    return "\n".join(lines)


def main() -> None:
    args = sys.argv[1:]
    profile = "--profile" in args
    states = [a for a in args if not a.startswith("--")]
    if len(states) == 1:
        print(bench(states[0], profile))
        return
    for state in states or STATES:
        cmd = [sys.executable, "-m", "tools.battle_bench", state, *(["--profile"] if profile else [])]
        subprocess.run(cmd, check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
