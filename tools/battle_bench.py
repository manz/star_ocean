"""Count the battle's late frames in kintsuki: the patched game (build/star_ocean.sfc + its IPS) runs a battle state
for 600 frames, A tapped every 10, and every pass of the battle loop (C1:0147, one per 2 frames at full speed) is
timed. A gap of 3 or 4 frames is a late pass; a gap of 1 catches up; lost = passes a 30 fps loop would have run
between the first and the last one, minus those that ran (a battle that ends early stops counting there).

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
LOOP = 0xC10147  # jsl to the battle update, once per pass
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
    start = emu.frame_count
    passes: list[int] = []
    emu.add_exec_callback(LOOP, LOOP, lambda _pc, _v: passes.append(emu.frame_count - start))
    excl: Counter[int] = Counter()
    incl: Counter[int] = Counter()
    heavy = 0
    for frame in range(FRAMES):
        emu.press(0, Button.A, frame % 10 < 3)
        if not profile:
            emu.run_frames(1)
            continue
        emu.profile_start()
        emu.run_frames(1)
        stats = emu.profile_stop()
        if sum(s.excl_cycles for s in stats if s.pc in WAITS) < 0.15 * FRAME_CYCLES:
            heavy += 1
            for s in stats:
                excl[s.pc] += s.excl_cycles
                incl[s.pc] += s.incl_cycles
    gaps = Counter(b - a for a, b in itertools.pairwise(passes))
    late = sum(n for gap, n in gaps.items() if gap >= 3)
    lost = (passes[-1] - passes[0]) // 2 + 1 - len(passes)
    lines = [f"{state}: {len(passes)} passes, {late} late, {gaps[1]} caught up, {lost} lost"]
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
