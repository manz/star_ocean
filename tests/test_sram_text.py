"""The patch's SRAM text routines against every scene of the base ROM (tools/check_sram_text.py)."""

from __future__ import annotations

import subprocess
import sys

import pytest

from tools.rom import DEFAULT_ROM, ROOT


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
def test_every_scene_unpacks_and_selects_through_sram() -> None:
    run = subprocess.run(
        [sys.executable, "-m", "tools.check_sram_text"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert run.returncode == 0, run.stdout + run.stderr
