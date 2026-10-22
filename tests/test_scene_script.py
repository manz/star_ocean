from tools.dialog import SCENES
from tools.scene_script import STRAY_TAIL_SCENES, Reader, disassemble, header, listing, scene_data


def value(raw: str) -> str:
    return str(Reader(bytes.fromhex(raw), 0, 0).value())


def test_immediate_byte() -> None:
    assert value("00 05") == "5"


def test_immediate_word() -> None:
    assert value("01 34 12") == "4660"


def test_variable_short_index() -> None:
    assert value("80 4c") == "var[0x4c]"


def test_variable_long_index() -> None:
    assert value("81 81 23") == "var.w[0x123]"


def test_system_variable() -> None:
    assert value("c1 08") == "sys.w[0x8]"


def test_run_of_bare_bytes() -> None:
    r = Reader(bytes.fromhex("f2 16 0d 05"), 0, 0)
    assert [str(r.value()) for _ in range(3)] == ["22", "13", "5"]


def test_scene_80_header_start_entry() -> None:
    assert header(scene_data(80)).entries[0].address == 0xA1


def test_every_scene_sweeps_to_its_end() -> None:
    tails = [s for s in range(1, SCENES + 1) if disassemble(scene_data(s))[1][-1].name == "db"]
    assert tails == STRAY_TAIL_SCENES


def test_scene_80_door_with_edit() -> None:
    door = next(i for i in disassemble(scene_data(80, True))[1] if i.offset == 0x396)
    assert door.operands[2] == "var[0x4c] == 4 && var[0x4d] == 3 && var[0x4c] == 4 && var[0x4f] == 2"


def test_set_renders_store() -> None:
    line = next(line for line in listing(scene_data(80), {}) if line.strip().startswith("00ca"))
    assert line.endswith("set var.w[0x38] &= 255")


def test_listing_shows_message_text() -> None:
    lines = listing(scene_data(80), {10: "Entrer les quatre lettres"})
    assert any(line.endswith("say_mode1 10  ; Entrer les quatre lettres") for line in lines)
