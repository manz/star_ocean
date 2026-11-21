"""The story graph read from the scene scripts (tools/story_graph.py, notes/text/map_table.md)."""

from __future__ import annotations

from pathlib import Path

from tools import save_slot
from tools.dialog import SCENES
from tools.map_table import map_scenes, scene_maps
from tools.story_graph import DEBUG_SCENE, export, graphs, main, scene_graph

SAVES = Path(__file__).parent / "saves"


def test_the_map_table_names_each_map_s_scene() -> None:
    scenes = map_scenes()
    assert (len(scenes), scenes[79], scenes[164], scene_maps()[9]) == (608, 3, 80, frozenset({22, 23, 24}))


def test_setups_test_the_maps_of_their_own_scene() -> None:
    """Three maps a scene tests for while their record names another scene: 548 (83, record 88), 559 (91, 90),
    578 (90, 93)."""
    scenes = map_scenes()
    elsewhere = {
        (g.scene, m)
        for g in graphs()
        for p in g.placements
        if len(p.maps) == 1
        for m in p.maps
        if scenes.get(m) != g.scene
    }
    assert elsewhere == {(83, 548), (91, 559), (90, 578)}


def test_every_exit_leads_to_a_map() -> None:
    scenes = map_scenes()
    assert all(e.to in scenes for g in graphs() for e in g.exits())


def test_laponia_exits() -> None:
    """Map 24's four doors; on map 22 the inn's door depends on the story, the north path only pushes back."""
    exits = scene_graph(9).exits()
    assert {(e.box, e.to) for e in exits if e.maps == {24}} == {
        ((32, 8, 33, 8), 29),
        ((37, 26, 38, 26), 30),
        ((40, 55, 45, 55), 49),
        ((6, 1, 8, 1), 50),
    }
    on_22 = {(e.box, e.to, " ".join(map(str, e.guards))) for e in exits if e.maps == {22}}
    assert ((32, 8, 33, 8), 25, "var.w[0x10] <= 11") in on_22
    assert ((32, 8, 33, 8), 26, "!(var.w[0x10] <= 11)") in on_22
    assert not any(box == (6, 1, 8, 1) for box, _, _ in on_22)


def test_the_calnus_holocube_room_exit() -> None:
    (e,) = (e for e in scene_graph(3).exits() if e.maps == {79})
    assert (e.box, e.to, e.x, e.y, e.facing) == ((8, 17, 9, 17), 71, 17, 14, 2)


def test_every_scene_walks() -> None:
    assert sum(len(scene_graph(s).exits()) for s in range(1, SCENES + 1)) > 1400


def test_cli_lists_a_map_s_exits() -> None:
    lines: list[str] = []
    main(["79"], lines.append)
    assert lines == ["scene  3 maps [79] (8, 17, 9, 17) -> 71 (17, 14)"]


SAVE_SLOTS = [
    (f.stem, n, save_slot.slot(f.read_bytes(), n))
    for f in sorted(SAVES.glob("*.srm"))
    for n in range(save_slot.SLOTS)
    if save_slot.used(save_slot.slot(f.read_bytes(), n))
]


def test_the_slot_layout_puts_the_story_where_the_loader_does() -> None:
    """C2:D53E wrote var.w[0x10] from slot + 0x2FD and the flags from + 0x2AD when a save loaded."""
    offsets = {address: offset for offset, _, address in save_slot.layout()}
    assert (offsets[save_slot.STORY], offsets[save_slot.FLAGS]) == (0x2FD, 0x2AD)


def test_the_counter_only_goes_up_over_the_saves() -> None:
    fantasyanime = [save_slot.story(data) for name, _, data in SAVE_SLOTS if name.startswith("fantasyanime")]
    assert fantasyanime == sorted(fantasyanime) and (fantasyanime[0], fantasyanime[-1]) == (43, 173)


def test_every_save_has_a_next_story_step() -> None:
    at = {s.at for g in graphs() if g.scene != DEBUG_SCENE for s in g.steps()}
    assert {(name, n) for name, n, data in SAVE_SLOTS if save_slot.story(data) not in at} == set()


def test_the_first_step_is_laponia_s_zone() -> None:
    """The start (12) moves on at the zone map 23's setup places only then."""
    lines: list[str] = []
    main(["--story", "12"], lines.append)
    assert lines == ["12 -> 13: scene 9 maps [23] step (9, 37, 14, 37)"]


def test_a_set_adds_to_the_counter() -> None:
    """Scene 17's `set var.w[0x10] += 2` at 98 (map 233's arrival)."""
    assert any((s.at, s.to) == (98, 100) for s in scene_graph(17).steps())


def test_the_export_carries_the_counter_each_exit_needs() -> None:
    """Map 22's inn door: map 25 up to 11, map 26 after."""
    data = export()
    exits = data["exits"]
    assert isinstance(exits, list)
    inn = {e["to"]: e["counter"] for e in exits if e["maps"] == [22] and e["box"] == [32, 8, 33, 8]}
    assert inn[25] == list(range(12)) and inn[26] == list(range(12, 256))


def test_a_flag_test_stored_in_a_system_variable_is_a_flag_guard() -> None:
    """Map 31's arrival at 46 (scene 7: `flag_test 1; store_result sys[8]; if sys.w[0x8] == 0`) needs flag 1 on."""
    (step,) = [s for s in scene_graph(7).steps() if s.at == 46]
    assert "flag[1]" in map(str, step.guards)


def test_the_export_lists_what_sets_each_flag() -> None:
    """Flag 1 comes on as scene 72's cutscene ends on map 14, at 41."""
    flags = export()["flags"]
    assert isinstance(flags, list)
    ones = [(f["scene"], f["maps"], f["on"], f["counter"]) for f in flags if f["flag"] == 1]
    assert ones == [(72, [14], True, [41])]
