"""Scene messages annotated with how the event scripts use them (tools/annotate.py)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from tools.annotate import annotate, choice, labels, menu_counts, scene_usage, trigger_name
from tools.rom import ROOT
from tools.scene_script import scene_data
from tools.scene_walk import walk


def attributes(scene: int, message: int, lang: str = "fr") -> dict[str, str]:
    root = ET.parse(ROOT / "text" / lang / f"scene_{scene:02d}.xml").getroot()
    node = next(n for n in root if n.get("id") == str(message))
    return {k: v for k, v in node.attrib.items() if k != "id"}


def test_annotations_are_up_to_date() -> None:
    """Rerun `python -m tools.annotate` after editing the scripts or adding messages."""
    assert annotate(write=False) == []


def test_portmith_pirate_menu() -> None:
    assert attributes(25, 49) == {"choice": "3", "window": "1", "trigger": "talk 20", "npc": "Ben le Marin"}


def test_japanese_names_the_npc_in_japanese() -> None:
    assert attributes(25, 49, "jp") == attributes(25, 49) | {"npc": "船乗りベン"}


def test_french_labels_skip_party_members_and_unknowns() -> None:
    text = "Ben le Marin[br]\nAhoy ![page]\n[nick:ラティ][br]\nSalut.[page]\n???[br]\nQui ?[page]\n[end]"
    assert labels(text, japanese=False) == ["Ben le Marin"]


def test_japanese_label_is_the_name_before_the_quote() -> None:
    assert labels("船乗りベン「よう。[page]\n[nick:ラティ]「うん。[page]\n[end]", japanese=True) == ["船乗りベン"]


def test_a_question_is_yes_no() -> None:
    assert attributes(25, 32)["choice"] == "yes-no"


def test_a_menu_whose_count_varies_is_dynamic() -> None:
    assert menu_counts(walk(scene_data(85, with_edits=True)).code)[17] == {2, 3, 4}
    assert choice({2, 3, 4}) == "dynamic" and choice({"var"}) == "dynamic"


def test_a_message_no_script_says_is_unused() -> None:
    assert attributes(44, 136) == {"unused": "1"}
    assert 136 not in scene_usage(scene_data(44, with_edits=True))


def test_trigger_names() -> None:
    assert [trigger_name(0, 18), trigger_name(1, 3), trigger_name(2, 0x7F), trigger_name(2, 0x7D)] == [
        "talk 18",
        "actor 3",
        "search",
        "touch",
    ]
    assert trigger_name(2, 4) == "tile 4"
