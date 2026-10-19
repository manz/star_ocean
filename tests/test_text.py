"""Script XML against the base ROM: every dump re-encodes to the exact original bytes."""

from __future__ import annotations

from pathlib import Path

import pytest
from script import Table
from script.pointers import read_pointers_from_xml

from tools import dump_text
from tools.dialog import SCENES, build_block, dialog_table, glyphs, messages, scene_block
from tools.menu_text import DATABASES, Strings, entries, table_for
from tools.rom import DEFAULT_ROM, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")


@pytest.fixture(scope="module")
def rom() -> Rom:
    return Rom()


@pytest.fixture(scope="module")
def dumped(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("jp")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("sys.argv", ["dump_text", "-o", str(out)])
        dump_text.main()
    return out


@pytest.fixture(scope="module")
def table() -> Table:
    return dialog_table()


def _values(path: Path, table: Table) -> list[bytes]:
    return [p.get_value() for p in sorted(read_pointers_from_xml(str(path), table), key=lambda p: p.id)]


def test_glyph_table_covers_every_glyph_once() -> None:
    table = glyphs()
    assert sorted(table) == list(range(0x640)) and len(set(table.values())) == 0x640


@pytest.mark.parametrize("scene", range(1, SCENES + 1))
def test_scene_xml_rebuilds_the_block(rom: Rom, dumped: Path, table: Table, scene: int) -> None:
    assert build_block(_values(dump_text.scene_path(dumped, scene), table)) == scene_block(rom, scene)


def test_block_split_is_lossless(rom: Rom) -> None:
    block = scene_block(rom, 4)
    assert build_block(messages(block)) == block


@pytest.mark.parametrize("db", DATABASES, ids=lambda d: d.name)
def test_database_xml_reencodes_every_string(rom: Rom, dumped: Path, db: Strings) -> None:
    # read_pointers_from_xml numbers from the written id minus one
    xml = {p.id + 1: p.get_value() for p in read_pointers_from_xml(str(dumped / f"{db.name}.xml"), table_for(db))}
    assert xml == {e.ids[0]: e.value for e in entries(rom, db)}


def test_speaker_names_render_as_tags(table: Table) -> None:
    assert table.to_text(bytes.fromhex("020c")) == "[name:ラティクス]"


def test_unknown_name_slot_keeps_its_argument(table: Table) -> None:
    assert table.to_text(bytes.fromhex("021d")) == "[str][0x1d]"


@pytest.mark.parametrize(
    ("name", "sid", "text"),
    [
        ("labels8", 0xEA6A, "とくぎ　　　　アイテム　　　せんじゅつ　　レジスト[end]"),
        ("battle16", 0x0001, "テストメッセージ[end]"),
        ("menu16", 0xEDE6, "特技[end]"),
    ],
)
def test_database_strings_read_as_on_screen(rom: Rom, name: str, sid: int, text: str) -> None:
    db = next(d for d in DATABASES if d.name == name)
    value = next(e.value for e in entries(rom, db) if sid in e.ids)
    assert table_for(db).to_text(value) == text
