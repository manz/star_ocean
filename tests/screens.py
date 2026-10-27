"""Drive the patched game in kintsuki and compare what it shows with golden images.

The emulator loads build/star_ocean.sfc (the base ROM link `tools/patch.py` writes) and soft-patches it with
build/star_ocean.ips. A state is a savestate under tests/states/; a screen is reached from it by button taps. A
golden missing on disk is recorded (the test skips: look at it, commit it); UPDATE_GOLDENS=1 records them all again.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest
from katsuji import png
from katsuji.png import Pixels

from tools.rom import ROOT

if TYPE_CHECKING:
    from kintsuki import Emu

ROM = ROOT / "build" / "star_ocean.sfc"
IPS = ROOT / "build" / "star_ocean.ips"
STATES = Path(__file__).parent / "states"
GOLDENS = Path(__file__).parent / "goldens"
PICTURE = np.s_[9 : 9 + 224, 13 : 13 + 256]  # the SNES picture inside kintsuki's framebuffer, [y, x]
HOLD, GAP = 4, 90  # frames a tap holds the button, then waits (menus animate their windows in)


def emulator(state: str, sram: bytes | None = None) -> Emu:
    """The patched game at tests/states/<state>.kss, one frame run so it has a picture. `sram` replaces the state's
    (an 8 KB .srm fills the start, the rest zeroed)."""
    if not ROM.exists() or not IPS.exists():
        pytest.skip("patch not built: uv run python -m tools.patch")
    kintsuki = pytest.importorskip("kintsuki")
    emu: Emu = kintsuki.Emu(load_srm_sidecar=False, sram_policy="fit")  # states saved with the app's 32 KB SRAM
    emu.load_rom(str(ROM))
    emu.load_state((STATES / f"{state}.kss").read_bytes())
    if sram is not None:
        emu.inject_sram(sram)
    emu.run_frames(1)
    return emu


def power_on(frames: int, sram: bytes | None = None) -> Emu:
    """The patched game run `frames` frames from power on, the cart holding `sram` (or nothing): screens a
    savestate cannot show, as one keeps the VRAM its build loaded."""
    if not ROM.exists() or not IPS.exists():
        pytest.skip("patch not built: uv run python -m tools.patch")
    kintsuki = pytest.importorskip("kintsuki")
    emu: Emu = kintsuki.Emu(load_srm_sidecar=False, sram_policy="fit")
    emu.load_rom(str(ROM))
    if sram is not None:
        emu.inject_sram(sram)
    emu.run_frames(frames)
    return emu


def tap(emu: Emu, buttons: str) -> None:
    """Press and release each of the comma-separated buttons (kintsuki.Button names) in turn."""
    from kintsuki import Button

    for name in filter(None, buttons.split(",")):
        button = getattr(Button, name)
        emu.press(0, button, True)
        emu.run_frames(HOLD)
        emu.press(0, button, False)
        emu.run_frames(GAP)


def rgb(path: Path) -> Pixels:
    """The PNG's pixels as (height, width, 3) RGB."""
    pixels, palette = png.read(path)
    if palette is not None:
        pixels = np.array(palette, dtype=np.uint8).reshape(-1, 3)[pixels]
    elif pixels.ndim == 2:
        pixels = np.stack([pixels] * 3, axis=-1)
    return np.ascontiguousarray(pixels[..., :3])


def picture(emu: Emu) -> Pixels:
    """The SNES picture, (224, 256, 3) RGB."""
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "frame.png"
        emu.screenshot(str(shot))
        return np.ascontiguousarray(rgb(shot)[PICTURE])


def changed_pixels(a: Pixels, b: Pixels) -> int:
    return int(np.any(a != b, axis=-1).sum())


def assert_matches_golden(emu: Emu, name: str) -> None:
    """The picture is tests/goldens/<name>.png, pixel for pixel; a mismatch leaves <name>.actual.png beside it."""
    golden = GOLDENS / f"{name}.png"
    actual = picture(emu)
    if not golden.exists() or os.environ.get("UPDATE_GOLDENS") == "1":
        golden.parent.mkdir(parents=True, exist_ok=True)
        png.write(golden, actual)
        pytest.skip(f"recorded {golden.name}: check it, commit it")
    bad = changed_pixels(rgb(golden), actual)
    if bad:
        png.write(golden.with_suffix(".actual.png"), actual)
    assert bad == 0, f"{bad} pixels differ from {golden.name}"
