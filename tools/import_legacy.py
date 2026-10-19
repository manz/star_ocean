"""Import the old French project's dialog (``<Tag>`` txt per scene block) into text/<lang>/scene_NN.xml.

Their files are named by the scene's text pointer (``00E841FC.txt``), one ``[PTn-offset]`` section per message
(the offset / 2 = our message index), body up to ``<End>``. Their dumper opens every body with a speaker line (empty when
there is none) and puts ``<Pause>`` on its own line; every other line break is a real newline.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from tools.dialog import SCENES, scene_text_ptr
from tools.rom import ROOT, Rom

ENCODING = "cp1252"
SECTION = re.compile(r"^\[PT\d+-([0-9A-F]+)\]\n", re.MULTILINE)  # the offset is authoritative: PT numbers drift
# Translator typos: a tag closed by "]" or not at all at line end, "[character 09]".
TAG = re.compile(
    r"<([A-Za-z_]+)((?: [0-9A-Fa-f]+)*)(?:[>\]]|(?=\n))|\[[Cc]haracter ([0-9A-Fa-f]{2})(?: [^\]\n]*)?(?:\]|(?=\n))"
)

NICKNAMES = [
    "ラティ",
    "ミリー",
    "ドーン",
    "ロニキス",
    "イリア",
    "シウス",
    "ヨシュア",
    "ティニーク",
    "マーヴェル",
    "アシュレイ",
    "ペリシー",
    "フィア",
]
NAMES = ["ラティクス", *NICKNAMES[1:]]

# Their tag -> our tag; args are copied as [0xNN] bytes.
SIMPLE = {
    "speed": "[speed]",
    "color": "[color]",
    "colour": "[color]",
    "center": "[pos]",
    "window_style": "[mode8]",
    "item": "[item]",
    "image": "[narration]",
    "num": "[var]",
    "condition": "[leader]",
    "substring": "[memberD]",
}
# Glyphs their table had no SJIS character for.
GLYPH_TAGS = {"note": "♪", "heart": "♥", "circle": "○", "male": "♂", "female": "♀"}


def character(slot: int) -> str:
    if slot < 12:
        return f"[nick:{NICKNAMES[slot]}]"
    if slot < 24:
        return f"[name:{NAMES[slot - 12]}]"
    return f"[str][0x{slot:x}]"


def _args(raw: str) -> str:
    out = []
    for word in raw.split():
        out += [f"[0x{int(word[i : i + 2], 16):x}]" for i in range(0, len(word), 2)]
    return "".join(out)


def _tag(match: re.Match[str]) -> str:
    if match.group(3) is not None:
        return character(int(match.group(3), 16))
    name, raw = match.group(1).lower(), match.group(2)
    if name in GLYPH_TAGS:
        return GLYPH_TAGS[name]
    if name == "character":
        return character(int(raw, 16))
    if name == "image" and raw.strip().endswith("01") and len(raw.strip()) == 4:
        return "[narration]" + _args(raw.strip()[:2]) + "[page]\n"  # their dumper folds the next [page] in
    return SIMPLE[name] + _args(raw)


def convert(body: str, *, speaker_newline: bool = True) -> str:
    """One message body (their syntax) -> our XML text, ``[end]`` included."""
    body = body.split("<End>", 1)[0] if "<End>" in body else body.split("<end>", 1)[0]
    body = body.removeprefix("\n")  # empty speaker line
    body = body.replace("<Star Empty>", "☆").replace("<Star Fill>", "★")
    body = body.replace("[<", "<")  # typo: "[<Speed 00>"
    body = re.sub(r"(?<![\[<])\b(Character [0-9A-Fa-f]{2}(?: [^\]\n]*)?\])", r"[\1", body)  # typo: no "["
    body = body.replace("’", "'")
    body = re.sub(r"\n?[<\[][Pp]ause[>\]]\n?\n?", "<Pause>", body)  # + the next page's empty speaker line
    if not speaker_newline:
        body = re.sub(r"((?:<Character [0-9A-Fa-f]+>|\[[Cc]haracter [^\]]*\]))\n", r"\1", body)
        body = body.replace("\n「", "「")  # plain-text speaker name, every page
    body = re.sub(r"<([^\x00-\x7f]+)>", r"\1", body.rstrip("\n"))  # <術>: a glyph their table guessed
    text = TAG.sub(lambda m: "[page]\n" if m.group(1) and m.group(1).lower() == "pause" else _tag(m), body)
    return text + "[end]"


def parse(path: Path, encoding: str = ENCODING) -> dict[int, str]:
    """Message index -> body."""
    raw = path.read_bytes().decode(encoding, errors="strict").replace("\r", "")
    parts = SECTION.split(raw)
    return {int(parts[i], 16) // 2: parts[i + 1] for i in range(1, len(parts), 2)}


def write_xml(texts: dict[int, str], path: Path) -> None:
    """Same layout as a816's ``write_pointers_as_xml``, for text that has no byte table yet."""
    with path.open("w", encoding="utf-8") as fd:
        fd.write('<?xml version="1.0" encoding="utf-8"?>\n<sn:script xmlns:sn="http://snes.ninja/ScriptNS">\n')
        for pid, text in sorted(texts.items()):
            fd.write(f'<sn:pointer id="{pid:d}">{escape(text)}</sn:pointer>\n\n')
        fd.write("</sn:script>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, help="directory of 00EXXXXX.txt files")
    ap.add_argument("-l", "--lang", default="fr")
    args = ap.parse_args()
    out = ROOT / "text" / args.lang
    out.mkdir(parents=True, exist_ok=True)
    rom, done = Rom(), 0
    for scene in range(1, SCENES + 1):
        src = args.source / f"00{scene_text_ptr(rom, scene):06X}.txt"
        if not src.exists():
            print(f"scene {scene}: no {src.name}")
            continue
        write_xml({i: convert(body) for i, body in parse(src).items()}, out / f"scene_{scene:02d}.xml")
        done += 1
    print(f"{done} scenes -> {out}")


if __name__ == "__main__":
    main()
