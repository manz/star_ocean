"""French dialog -> scene text blocks for the patch.

Each text/fr/scene_NN.xml is encoded with text/so_fr.tbl (+ the control table), laid out as a block (offsets
then messages) and packed into the game's 0x81 LZSS container. Writes build/gen/scene_text/NN.bin and
build/gen/scene_text.i, which places every block in ROM pages 6-7 and repoints the scene table.
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

from script import Table
from script.pointers import read_pointers_from_xml

from tools import party_names
from tools.dialog import CONTROLS, SCENE_TABLE, SCENES, build_block, messages, scene_block
from tools.reflow import DialogLayout
from tools.rom import ROOT, Rom

TABLE = ROOT / "text" / "so_fr.tbl"
GEN = ROOT / "build" / "gen"
SRAM_TEXT = 0x5000  # src/dialog/sram_text.s: sram_text
SCENE_RECORD, TEXT_POINTER = 6, 3  # scene table: event pointer, then text pointer


WINDOW, MIN_MATCH, MAX_MATCH = 0xFFF, 3, 18
CHAIN = 64  # candidates tried per position


def fr_table() -> Table:
    table = Table(str(TABLE))
    table.include(str(CONTROLS))
    return table


def _longest(data: bytes, pos: int, chain: list[int]) -> tuple[int, int]:
    best_len = best_dist = 0
    limit = min(MAX_MATCH, len(data) - pos)
    for start in reversed(chain[-CHAIN:]):
        dist = pos - start
        if dist > WINDOW:
            break
        length = 0
        while length < limit and data[start + length] == data[pos + length]:
            length += 1
        if length > best_len:
            best_len, best_dist = length, dist
            if length == limit:
                break
    return best_len, best_dist


def lzss(data: bytes) -> bytes:
    """Greedy LZSS as `unpack` reads it: flag byte (bit 0 first, 1 = literal), references `dd ld`."""
    out, chains = bytearray(), dict[bytes, list[int]]()
    pos = 0
    while pos < len(data):
        flags_at, flags = len(out), 0
        out.append(0)
        for bit in range(8):
            if pos >= len(data):
                break
            length, dist = _longest(data, pos, chains.get(data[pos : pos + MIN_MATCH], []))
            step = length if length >= MIN_MATCH else 1
            if step == 1:
                flags |= 1 << bit
                out.append(data[pos])
            else:
                out += bytes([dist & 0xFF, dist >> 8 | (length - MIN_MATCH) << 4])
            for p in range(pos, pos + step):
                chains.setdefault(data[p : p + MIN_MATCH], []).append(p)
            pos += step
        out[flags_at] = flags
    return bytes(out)


def container(data: bytes) -> bytes:
    packed = lzss(data)
    head = bytes([0x81]) + len(packed).to_bytes(2, "little") + b"\0\0" + len(data).to_bytes(2, "little") + b"\0\0"
    return head + packed


def scene_values(
    path: Path, table: Table, japanese: list[bytes], layout: Callable[[str], str] | None = None
) -> tuple[list[bytes], list[int]]:
    """The scene's messages by index, each laid out by `layout`; a message the French lacks keeps the Japanese
    bytes."""
    pointers = read_pointers_from_xml(str(path), table, layout)
    french = {p.id + 1: p.get_value() for p in pointers}  # reader: id - 1
    values = [french.get(i, jp) for i, jp in enumerate(japanese)]
    return values, [i for i in range(len(japanese)) if i not in french]


def menu_errors(path: Path, layout: DialogLayout) -> list[str]:
    """Each counted menu of the scene (`choice="N"`, tools/annotate.py) against its option lines."""
    out = []
    for node in ET.parse(path).getroot():
        count = node.get("choice", "")
        if count.isdigit():
            errors = layout.menu_errors(node.text or "", int(count))
            out += [f"{path.stem} message {node.get('id')}: {error}" for error in errors]
    return out


def build(source: Path, out: Path) -> list[str]:
    rom, table = Rom(), fr_table()
    layout = DialogLayout(party_names.inserts())
    (out / "scene_text").mkdir(parents=True, exist_ok=True)
    lines, report, menus = [], [], []
    for scene in range(1, SCENES + 1):
        path = source / f"scene_{scene:02d}.xml"
        if not path.exists():
            report.append(f"scene {scene}: no French, Japanese kept")
            continue
        menus += menu_errors(path, layout)
        wide: list[str] = []

        def laid_out(text: str) -> str:
            out = layout.message(text)
            wide.extend(layout.overflows(out))  # noqa: B023 - called within this iteration
            return out

        values, kept = scene_values(path, table, messages(scene_block(rom, scene)), laid_out)
        report += [f"scene {scene}: line too wide, {line}" for line in wide]
        block = build_block(values)
        if len(block) > SRAM_TEXT:
            raise ValueError(f"scene {scene}: {len(block)} bytes, SRAM holds {SRAM_TEXT}")
        name = f"{scene:02d}.bin"
        (out / "scene_text" / name).write_bytes(container(block))
        pointer = SCENE_TABLE + (scene - 1) * SCENE_RECORD + TEXT_POINTER
        lines += [
            f".alloc scene_text_{scene:02d} in rom_pages_67 {{",
            f'    .incbin "scene_text/{name}"',
            "}",
            f".alloc at 0x{pointer:06X} size 3 {{",
            f"    .dl scene_text_{scene:02d}",
            "}",
        ]
        if kept:
            report.append(f"scene {scene}: Japanese kept for messages {kept}")
    if menus:
        raise ValueError("menus that would not show one line per option:\n" + "\n".join(menus))
    (out / "scene_text.i").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path, nargs="?", default=ROOT / "text" / "fr")
    args = ap.parse_args()
    for line in build(args.source, GEN):
        print(line)


if __name__ == "__main__":
    main()
