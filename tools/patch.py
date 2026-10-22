"""Build the a816 patch, plus a link to the base ROM beside it that kintsuki soft-patches at load.

kintsuki applies `<rom-without-extension>.ips` when it loads a ROM, so `build/star_ocean.sfc` (a link to the base
ROM) runs with `build/star_ocean.ips`. No patched ROM is written.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from a816.module_builder import build_with_imports
from katsuji import build as katsuji_build
from katsuji import config as katsuji_config

from tools import (
    badge,
    encode_menus,
    encode_text,
    menu_font,
    menu_font16,
    renders,
    vwf8,
    yes_no,
)
from tools.rom import DEFAULT_ROM, ROOT

BUILD = ROOT / "build"
GEN = BUILD / "gen"
DIALOG_FONT_GLYPHS, DIALOG_FONT_RECORD = 0x80, 17  # src/dialog/vwf.s: FONT_GLYPHS, FONT_RECORD


@dataclass(frozen=True)
class Patch:
    ips: Path
    rom: Path
    symbols: dict[str, int]


def build_assets() -> None:
    """katsuji fonts, the slice of the dialog font the patch holds (codes below 0x80), French text, menus, narration, cutscenes, badge, yes / no bubbles."""
    katsuji_build.build(katsuji_config.load(ROOT / "katsuji.toml"))
    font = (GEN / "dialog_font.dat").read_bytes()
    (GEN / "dialog_font_low.bin").write_bytes(font[: DIALOG_FONT_GLYPHS * DIALOG_FONT_RECORD])
    encode_text.build(ROOT / "text" / "fr", GEN)
    menu_font.build(out=GEN / "menu_font8.bin")
    menu_font16.build(out=GEN)
    encode_menus.build(ROOT / "text" / "fr", GEN)
    renders.build(GEN)
    badge.build(out=GEN)
    yes_no.build(out=GEN)
    vwf8.build(out=GEN)


def build(out: Path = BUILD) -> Patch:
    build_assets()
    ips = out / "star_ocean.ips"
    result = build_with_imports(
        main_source=ROOT / "star_ocean.s",
        output_file=ips,
        module_paths=[ROOT / "src"],
        output_dir=out / "obj",
        include_paths=[ROOT / "src", ROOT / "build" / "gen"],
        overlap_mode="error",
    )
    if result.exit_code != 0:
        raise RuntimeError("\n".join(result.diagnostics) or "a816 build failed")
    rom = ips.with_suffix(".sfc")
    rom.unlink(missing_ok=True)
    rom.symlink_to(DEFAULT_ROM.resolve())
    return Patch(ips, rom, result.symbol_map)


def main() -> None:
    patch = build()
    print(f"{patch.ips} -> {patch.rom}")


if __name__ == "__main__":
    main()
