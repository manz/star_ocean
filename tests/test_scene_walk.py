from tools.dialog import SCENES
from tools.scene_script import disassemble, scene_data
from tools.scene_walk import dead_messages, main, missing_entries, walk


def test_walked_code_lands_on_the_sweep() -> None:
    """Every instruction the walk reaches starts where the linear sweep put one."""
    stray = []
    for scene in range(1, SCENES + 1):
        data = scene_data(scene)
        starts = {i.offset for i in disassemble(data)[1]}
        stray += [(scene, off) for off in walk(data).code if off not in starts]
    assert stray == []


def test_nearly_everything_is_reached() -> None:
    reached = total = 0
    for scene in range(1, SCENES + 1):
        w = walk(scene_data(scene))
        reached, total = reached + w.reached_bytes(), total + w.end - w.start
    assert reached / total > 0.99


def test_scene_94_names_a_missing_entry() -> None:
    data = scene_data(94)
    assert missing_entries(data, walk(data)) == [(0xDA, 2, 0x20)]


def test_scene_11_dead_block_holds_messages() -> None:
    assert dead_messages(scene_data(11), 0x123C, 0x145E) == list(range(56, 68))


def test_cli_totals() -> None:
    lines: list[str] = []
    main(["80"], lines.append)
    assert lines[-1].startswith("all: ")
