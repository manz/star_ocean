"""`text/scenes.xml` (tools/scenes.py): a scene per scene file, titled by its banner, its messages by trigger."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("katsuji.script.sn", reason="katsuji with sn:script reading")

from tools.scenes import SCENES, TEXT, document, scene, title

HEAD = '<?xml version="1.0" encoding="utf-8"?>\n<sn:script xmlns:sn="http://snes.ninja/ScriptNS">\n'


def script(tmp_path: Path, *pointers: str) -> Path:
    path = tmp_path / "scene_05.xml"
    path.write_text(HEAD + "".join(pointers) + "</sn:script>\n", encoding="utf-8")
    return path


def say(id_: int, text: str, **attributes: str) -> str:
    attrs = "".join(f' {name}="{value}"' for name, value in attributes.items())
    return f'<sn:pointer id="{id_}"{attrs}>{text}</sn:pointer>\n'


def test_a_banner_places_its_scene(tmp_path: Path) -> None:
    path = script(tmp_path, say(0, "[center]Clatos[page]\n[end]", trigger="start"))
    assert 'place="scene_05:0"' in scene(path)


def test_a_scene_with_no_banner_is_titled_by_its_file(tmp_path: Path) -> None:
    assert 'title="scene 05">' in scene(script(tmp_path, say(0, "Salut[end]", trigger="start")))


def test_an_unused_message_is_left_out(tmp_path: Path) -> None:
    path = script(tmp_path, say(0, "Salut[end]", trigger="start", unused="1"))
    assert "scene_05:0" not in scene(path)


def test_the_start_comes_before_the_npcs(tmp_path: Path) -> None:
    path = script(tmp_path, say(0, "Salut[end]", trigger="talk 3"), say(1, "Bonjour[end]", trigger="start"))
    out = scene(path)
    assert out.index('"start"') < out.index('"talk 3"')


def test_npcs_go_by_number(tmp_path: Path) -> None:
    path = script(tmp_path, say(0, "A[end]", trigger="talk 12"), say(1, "B[end]", trigger="talk 3"))
    out = scene(path)
    assert out.index('"talk 3"') < out.index('"talk 12"')


def test_an_npc_trigger_is_named_by_its_npc() -> None:
    from katsuji.script.sn import Message

    assert title("talk 20", [Message("scene_05", "0", "", {"npc": "Puffy"})]) == "talk 20 · Puffy"


def test_tiles_read_as_ranges() -> None:
    assert title("tile 1 tile 2 tile 3 tile 5", []) == "tiles 1-3, 5"


def test_mixed_triggers_read_as_written() -> None:
    assert title("tile 1 talk 2", []) == "tile 1 talk 2"


def test_the_document_holds_every_scene(tmp_path: Path) -> None:
    assert document([script(tmp_path, say(0, "A[end]", trigger="start"))]).count("<sn:scene title=") == 2


def test_scenes_xml_is_up_to_date() -> None:
    expected = document(sorted((TEXT / "fr").glob("scene_*.xml")))
    assert SCENES.read_text(encoding="utf-8") == expected, "run python -m tools.scenes"
