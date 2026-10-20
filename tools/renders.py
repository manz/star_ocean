"""The narration, cutscene and title menu text renders, tracked in src_assets/renders/ for machines without the
macOS fonts.

tools/narration.py, tools/cutscene_text.py and tools/title_menu.py draw with /System/Library/Fonts (Helvetica, Times),
which only macOS has. Where the fonts are, the build renders as usual and refreshes the tracked copy of what a816
reads (the .i and .bin files); elsewhere (CI) it copies them back into build/gen. `inputs.sha256` hashes the renders'
inputs, so a copy older than the text or the tools fails the build instead of shipping.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from tools import cutscene_text, narration, title_menu
from tools.rom import ROOT

RENDERS = ROOT / "src_assets" / "renders"
STAMP = "inputs.sha256"
INPUTS = (
    ROOT / "text" / "fr" / "narration.toml",
    ROOT / "text" / "fr" / "cutscenes.toml",
    ROOT / "text" / "fr" / "title_menu.toml",
    ROOT / "tools" / "narration.py",
    ROOT / "tools" / "cutscene_text.py",
    ROOT / "tools" / "title_menu.py",
)
PATTERNS = (
    "narration.i",
    "narration_*.bin",
    "cutscenes.i",
    "cutscene_*.bin",
    "credit_title_*.bin",
    "title_menu.i",
    "title_sheet.bin",
)


def fonts_present() -> bool:
    return narration.FONT.exists() and all(style[0].exists() for style in cutscene_text.STYLES.values())


def stamp(inputs: tuple[Path, ...] = INPUTS) -> str:
    digest = hashlib.sha256()
    for path in inputs:
        digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0" + path.read_bytes())
    return digest.hexdigest() + "\n"


def outputs(directory: Path) -> list[Path]:
    return sorted(path for pattern in PATTERNS for path in directory.glob(pattern))


def build(gen: Path, renders: Path = RENDERS) -> None:
    """Render into `gen` and refresh `renders`, or, without the fonts, copy `renders` into `gen`."""
    if fonts_present():
        narration.build(out=gen)
        cutscene_text.build(out=gen)
        title_menu.build(out=gen)
        if renders.exists():
            shutil.rmtree(renders)
        renders.mkdir(parents=True)
        for path in outputs(gen):
            shutil.copy2(path, renders / path.name)
        (renders / STAMP).write_text(stamp())
        return
    if not (renders / STAMP).exists() or (renders / STAMP).read_text() != stamp():
        raise RuntimeError(f"{renders} is older than the text it renders: rebuild on macOS and commit it")
    gen.mkdir(parents=True, exist_ok=True)
    for path in outputs(renders):
        shutil.copy2(path, gen / path.name)
