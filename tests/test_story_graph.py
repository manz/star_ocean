"""The story graph read from the scene scripts (tools/story_graph.py, notes/text/map_table.md)."""

from __future__ import annotations

from tools.dialog import SCENES
from tools.map_table import map_scenes, scene_maps
from tools.story_graph import graphs, main, scene_graph


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
