"""tools.compare: Japanese and French entries matched by id."""

from __future__ import annotations

from pathlib import Path

from tools.compare import Pair, pairs, parse_ids, render, select, source

JP = '<sn:script><sn:pointer id="1">バダム「いらっしゃい[page]\n[end]</sn:pointer>\n<sn:pointer id="2">[end]</sn:pointer>'
FR = '<sn:strings><sn:pointer id="1">Badam[br]\nBienvenue.[page]\n[end]</sn:pointer></sn:strings>'


def write(root: Path) -> Path:
    for lang, text in (("jp", JP), ("fr", FR)):
        (root / lang).mkdir()
        (root / lang / "scene_22.xml").write_text(text, encoding="utf-8")
    return root


def test_a_scene_number_names_its_file() -> None:
    assert source("22") == "scene_22"


def test_entries_pair_by_id_without_the_end(tmp_path: Path) -> None:
    assert pairs("scene_22", write(tmp_path))[0] == Pair(1, "バダム「いらっしゃい[page]", "Badam[br]\nBienvenue.[page]")


def test_an_id_only_in_japanese_pairs_with_nothing(tmp_path: Path) -> None:
    assert pairs("scene_22", write(tmp_path))[1] == Pair(2, "", "")


def test_ranges_take_hex_and_decimal() -> None:
    assert parse_ids(["0xFB90-0xFB92", "7"]) == {0xFB90, 0xFB91, 0xFB92, 7}


def test_grep_matches_either_side() -> None:
    rows = [Pair(1, "バダム", "Badam"), Pair(2, "イリア", "Iria")]
    assert select(rows, set(), "Iria") == [rows[1]]


def test_continuation_lines_line_up_under_the_text() -> None:
    assert render(Pair(1, "a", "b\nc"), hexadecimal=False) == "=== 1\nJP: a\nFR: b\n    c"
