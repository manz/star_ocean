"""The old French project's tag syntax -> ours (formats checked against their JP dump vs the ROM)."""

from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

from tools.dialog import CONTROLS
from tools.import_legacy import convert
from tools.reflow import BREAK, CENTER
from tools.rom import ROOT


@pytest.mark.parametrize(
    ("body", "ours"),
    [
        ("\n<Speed 03>Bonjour.\n<Pause>\n<End>\n\n", "[speed][0x3]Bonjour.[page]\n[end]"),
        ("[Character 01 Milly]\nAttends !\n<Pause>\n<End>\n", "[nick:ミリー]\nAttends ![page]\n[end]"),
        ("<Center 4400>Ville\n<Pause>\n<End>", "[pos][0x44][0x0]Ville[page]\n[end]"),
        ("Un\n<Pause>\n\nDeux\n<Pause>\n<End>", "Un[page]\nDeux[page]\n[end]"),
        ("<Image 0101>\n<End>", "[narration][0x1][page]\n[end]"),
        ("<Note><Heart><Star Fill>\n<End>", "♪♥★[end]"),
        ("<Color 04]Crat<Color 02>\n<End>", "[color][0x4]Crat[color][0x2][end]"),
        ("[Character 0C Ratix] !\n<End>", "[name:ラティクス] ![end]"),
        ("père de Character 05 Cius] ?\n<End>", "père de [nick:シウス] ?[end]"),
        ("tout s’arrête.\n<End>", "tout s'arrête.[end]"),
    ],
)
def test_convert(body: str, ours: str) -> None:
    assert convert(body) == ours


def test_jp_speaker_line_is_cosmetic() -> None:
    assert (
        convert("<Character 01>\n「やあ\n<Pause>\n<End>", speaker_newline=False) == "[nick:ミリー]「やあ[page]\n[end]"
    )


def _known_tags() -> set[str]:
    lines = CONTROLS.read_text(encoding="utf-8").splitlines()
    return {m for line in lines for m in re.findall(r"\[[^\]]*\]", line.split("=", 1)[1])}


@pytest.mark.parametrize("path", sorted((ROOT / "text" / "fr").glob("scene_*.xml")), ids=lambda p: p.stem)
def test_french_scenes_use_known_tags(path: Path) -> None:
    known = _known_tags() | {BREAK.removesuffix("\n"), CENTER}  # reflow's own tags, not game codes
    texts = [e.text or "" for e in ElementTree.parse(path).getroot()]
    unknown = {t for text in texts for t in re.findall(r"\[[^\]]*\]", text) if t not in known}
    assert not {t for t in unknown if not re.fullmatch(r"\[0x[0-9a-f]+\]", t)}
