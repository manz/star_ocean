"""The story graph read from the scene scripts (tools/story_graph.py, notes/text/map_table.md)."""

from __future__ import annotations

from pathlib import Path

from tools import save_slot
from tools.dialog import SCENES
from tools.map_table import map_scenes, scene_maps
from tools.story_graph import DEBUG_SCENE, clearings, export, gate_actions, graphs, main, scene_graph

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


def test_a_lower_bound_pins_the_step_to_it() -> None:
    """Scene 25: Ashlay's choice past `!(var.w[0x10] < 59)` moves 59 on to 60."""
    assert any((s.at, s.to) == (59, 60) for s in scene_graph(25).steps())


def test_a_trigger_that_clears_walls_is_an_opener() -> None:
    """Map 123's door: zone (23, 35)-(24, 35) clears the cells above it on the third hit."""
    assert any(a.trigger.box == (23, 35, 24, 35) for a in clearings(scene_graph(27)))


def test_the_silex_blows_the_gas_on_map_129() -> None:
    """Scene 27's A script: the Silex equipped, in a gas zone (var.w[0xa] set), flag 19 opens the east wall."""
    uses = {
        (a.trigger.box, a.trigger.item)
        for a in scene_graph(27).actions()
        if a.trigger.kind == "use" and a.name == "flag_on" and a.args[0] == 19
    }
    assert uses == {((22, 5, 22, 7), 510), ((23, 5, 23, 7), 510)}


def test_the_export_lists_where_the_silex_is_found() -> None:
    """Map 125: the zone before Velcant's fight."""
    items = export()["items"]
    assert isinstance(items, list)
    assert any(i["item"] == 510 and i["maps"] == [125] and i["trigger"]["box"] == [15, 14, 29, 14] for i in items)


def test_map_126_s_cell_gates_open_when_talked_to() -> None:
    assert {a.trigger.actor for a in gate_actions(scene_graph(27)) if 126 in a.maps} == {34, 35, 36, 37}


def test_the_boat_to_astral_is_a_talk_exit() -> None:
    """Map 83's boatman (actor 20), past the Yes: map 144."""
    assert any(e.actor == 20 and e.to == 144 and 83 in e.maps for e in scene_graph(25).talk_exits())


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


def test_an_unguarded_sibling_exit_gets_the_complement() -> None:
    """Map 179's south edge: to 192 unless the hero came from 174 or 180, to 180 when it did."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    south = {e["to"]: e["guards"] for e in exits if e["maps"] == [179] and e["box"] == [1, 31, 14, 31]}
    assert south[180] == ["var.w[0x23] == 174 || var.w[0x23] == 180"]


def test_a_wall_switch_sets_its_flag_through_a_variable() -> None:
    """Map 234's switch: `set var.w[0x4f] = 55`, A facing it in (14, 7) (its box holds half of 15), Yes: `flag_on
    var.w[0x4f]`."""
    flags = export()["flags"]
    assert isinstance(flags, list)
    switch = [f for f in flags if f["flag"] == 55 and f["on"]]
    assert [(f["maps"], f["trigger"]["kind"], f["trigger"]["box"]) for f in switch] == [([234], "use", [14, 7, 14, 7])]


def test_an_exit_walled_until_a_flag_needs_it() -> None:
    """Map 233's door to 235: the setup walls it unless flag 55 is on."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    assert [e["flags"] for e in exits if e["maps"] == [233] and e["to"] == 235] == [{"55": True}]


def test_the_export_lists_walls_a_flag_opens() -> None:
    """Map 239's ways north: walled until the switches on 242 (flag 56) and 243 (flag 57)."""
    walls = export()["walls"]
    assert isinstance(walls, list)
    north = [(w["flags"], w["box"]) for w in walls if w["maps"] == [239]]
    assert north == [({"56": True}, [7, 24, 8, 24]), ({"57": True}, [7, 40, 8, 40])]


def test_a_wall_two_flag_states_open_is_listed_twice() -> None:
    """Map 158's x 28: open with the switch's flag 102 on, or with plate 69's flag 99 off and 102 off."""
    walls = export()["walls"]
    assert isinstance(walls, list)
    ways = [w["flags"] for w in walls if w["maps"] == [158] and w["box"] == [28, 41, 28, 43]]
    assert sorted(ways, key=len) == [{"102": True}, {"99": False, "102": False}]


def test_a_zone_placed_at_two_counter_values_keeps_both() -> None:
    """Map 203's zone to map 507 is placed when the counter is 93 and when it is 109: a meet of the two paths kept
    neither."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    zone = {(tuple(e["counter"] or ()), e["to"]) for e in exits if e["maps"] == [203] and e["to"] == 507}
    assert zone == {((93,), 507), ((109,), 507)}


def test_an_arrival_step_takes_the_counter_of_the_exits_into_its_map() -> None:
    """Map 507's cutscene sets the counter to 111 on arrival; map 203's zone at 109 leads there."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    assert (109, 111) in {(s["at"], s["to"]) for s in steps if s["maps"] == [507]}


def test_exits_split_on_a_test_fold_back() -> None:
    """Map 79's door, reached through `flag[146]` and through `!flag[146]` on both sides of a counter test."""
    (e,) = (e for e in scene_graph(3).exits() if e.maps == {79})
    assert not e.guards


def test_a_test_on_a_variable_the_script_set_is_no_guard() -> None:
    """Map 507's cutscene counts `var[0x40]` to 32 before it sets the counter: the step needs nothing of it."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    assert all(not s["guards"] for s in steps if s["maps"] == [507])


def test_an_exit_carries_the_variables_its_script_set() -> None:
    """Map 58's west edge sets `var[0x25]` to 0 on its way into 57: 57's east edge then leads back to 58, not 62."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    west = [e for e in exits if e["maps"] == [58] and e["to"] == 57 and e["box"] == [0, 8, 0, 12]]
    assert [e["sets"] for e in west] == [{"var[0x25]": 0}]


def test_an_arrival_step_that_tests_where_the_hero_stands_has_a_landing() -> None:
    """Map 466 at 129 moves the story when the hero lands at x 184, feet 240: the landing from 463 (23, 32)."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    at = [s for s in steps if s["maps"] == [466] and s["at"] == 129]
    assert [(s["landing"], s["guards"]) for s in at] == [([23, 32], ["var.w[0x10] == 129"])]


def test_a_test_chain_into_one_branch_keeps_either_value() -> None:
    """Map 471's way back to 469: `== 13` and `== 14` both jump to the (27, 40) landing; the hole sets the column."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    hole = [e for e in exits if e["maps"] == [469] and e["box"] == [13, 19, 14, 19]]
    back = [e for e in exits if e["maps"] == [471] and (e["x"], e["y"]) == (27, 40)]
    assert [e["sets"] for e in hole] == [{"var.w[0x3c]": "x"}]
    assert all("var.w[0x3c] == 13 || var.w[0x3c] == 14" in e["guards"] for e in back)


def test_flags_packed_in_a_variable_wall_an_exit() -> None:
    """Map 469's way north opens when flags 83-89 read 29 (0011101): the exit needs each of them so."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    north = [e for e in exits if e["maps"] == [469] and e["to"] == 470]
    want = {"83": False, "84": False, "85": True, "86": True, "87": True, "88": False, "89": True}
    assert [e["flags"] for e in north] == [want]


def test_a_step_on_two_flag_results_needs_both_flags() -> None:
    """Map 84 at 137: `flag_test 93; flag_test 94; if sys.w[0x8] && sys.w[0x9]` moves on to 140, else back to 133."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    on = [s["flags"] for s in steps if s["maps"] == [84] and s["at"] == 137 and s["to"] == 140]
    assert on == [{"93": True, "94": True}]


def test_a_flag_result_anded_with_the_counter_is_a_flag_guard() -> None:
    """Map 87 at 133: `flag_test 92; if var.w[0x10] == 133 && sys.w[0x8] == 0` moves on to 137 with flag 92 off."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    on = [s["flags"] for s in steps if s["maps"] == [87] and s["at"] == 133 and s["to"] == 137]
    assert on == [{"92": False}]


def test_a_party_lookup_is_named_for_its_character() -> None:
    """Map 222 at 133: `char_party_pos 1; store_result sys[8]` moves on to 134 only with character 1 away."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    guards = [s["guards"] for s in steps if s["maps"] == [222] and s["at"] == 133 and s["to"] == 134]
    assert guards == [["var[0x13] == 0 && var.w[0x10] == 133 && party[1] == 0"]]


def test_a_choice_answer_is_named_choice() -> None:
    """Port 83's boatman: `choose 0, 4; store_result sys[8]; set var.w[0x46] = sys.w[0x8]`, the third line sails to
    Ecdart (156)."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    boat = [e["guards"] for e in exits if e["maps"] == [83] and e["actor"] == 20 and e["to"] == 156]
    assert boat and all("choice == 3" in g for g in boat)


def test_an_engraving_read_with_a_moves_the_story() -> None:
    """Map 164 at 143: A facing the engraving in its box (scene 80's A script, `actor_in_box`) moves the story on."""
    steps = export()["steps"]
    assert isinstance(steps, list)
    assert [s["trigger"] for s in steps if s["maps"] == [164] and s["at"] == 143] == [
        {"kind": "use", "box": [4, 4, 4, 4], "actor": None, "item": None}
    ]


def test_a_box_thinner_than_a_cell_is_the_cell_a_hero_on_the_grid_stands_in() -> None:
    """Map 158's switch: 8 px x 59 to 60, A only where the hero's x is cell 30."""
    flags = export()["flags"]
    assert isinstance(flags, list)
    switch = [f["trigger"]["box"] for f in flags if f["flag"] == 102 and f["on"] and f["maps"] == [158]]
    assert switch == [[30, 44, 30, 44]]


def test_a_map_change_takes_the_hero_before_one_it_runs_into() -> None:
    """Map 312's door: from 315 or 320 the script changes to 320, then runs on into the change to 324; only the first
    takes the hero."""
    exits = export()["exits"]
    assert isinstance(exits, list)
    to_324 = [e["guards"] for e in exits if e["maps"] == [312] and e["to"] == 324]
    assert to_324 == [["!(var.w[0x23] == 315)", "!(var.w[0x23] == 320)"]]


def test_a_wall_reads_flag_results_copied_into_variables() -> None:
    """Map 544's door: flags 119 to 123 tested, each result copied into `var.w[0x38]` on, then all of them anded."""
    walls = export()["walls"]
    assert isinstance(walls, list)
    door = [w["flags"] for w in walls if w["maps"] == [544]]
    assert door == [{str(f): True for f in range(119, 124)}]
