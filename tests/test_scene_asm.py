import pytest

from tools.dialog import SCENES
from tools.scene_asm import assemble, assign, condition, encode, encode_header, encode_value, imm, op, term, var
from tools.scene_script import Value, disassemble, instruction, scene_data


@pytest.mark.parametrize("edits", [False, True])
def test_every_scene_reencodes_to_its_bytes(edits: bool) -> None:
    mismatched = []
    for scene in range(1, SCENES + 1):
        data = scene_data(scene, edits)
        head, code = disassemble(data)
        if encode_header(head) + b"".join(encode(i, head.length) for i in code) != data:
            mismatched.append(scene)
    assert mismatched == []


def test_immediates_take_the_smallest_width() -> None:
    assert [encode_value(imm(n)).hex(" ") for n in (0, 255, 256)] == ["00 00", "00 ff", "01 00 01"]


def test_wide_index() -> None:
    assert encode_value(var(0x123, 1)).hex(" ") == "81 81 23"


def test_jumps_resolve_labels_from_the_header_end() -> None:
    code, labels = assemble(["loop", op("wait", 1), op("goto", "loop")], base=0x1D)
    assert (code.hex(" "), labels) == ("13 00 01 04 00 00", {"loop": 0x1D})


def test_labels_after_code_count_its_size() -> None:
    code, labels = assemble([op("goto", "end"), op("say_mode1", 9), "end", op("end")], base=0x10)
    assert (code.hex(" "), labels["end"]) == ("04 05 00 25 09 ff", 0x15)


def test_assign_matches_the_game_bytes() -> None:
    """Scene 80 at 0xca: `set var.w[0x38] &= 255`, the 255 a word."""
    ins = assign(var(0x38, 1), Value("imm", 255, 1), store="&=")
    assert encode(ins, 0) == scene_data(80)[0xCA:0xD1]


def test_assign_disassembles_back() -> None:
    raw = encode(assign(var(0x46, 1), var(0x46, 1), 2, "*", 1, "+"), 0)
    assert instruction(raw, 0, 0).operands == ["var.w[0x46] = var.w[0x46] 2 * 1 +"]


def test_condition_matches_the_scene_80_door() -> None:
    door = condition(*(term(var(i), "==", n) for i, n in ((0x4C, 4), (0x4D, 3), (0x4C, 4), (0x4F, 2))))
    ins = op("if", 0, 0, door)
    assert encode(ins, 0)[5:] == scene_data(80, True)[0x39B:0x3B3]


def test_operand_count_is_checked() -> None:
    with pytest.raises(ValueError, match="wait takes 1 operands"):
        op("wait")


def test_narrow_index_refuses_a_large_number() -> None:
    with pytest.raises(ValueError, match="two bytes"):
        encode_value(Value("var", 0x80))
