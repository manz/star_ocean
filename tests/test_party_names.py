"""Party name records (tools/party_names.py, src/dialog/names.s): new game defaults, older saves' names."""

from __future__ import annotations

from pathlib import Path

import pytest
from katsuji.script import Table

from tests.screens import emulator, tap
from tools.encode_menus import TABLE
from tools.party_names import RECORD, defaults, dejap_names, inserts, record
from tools.rom import DEFAULT_ROM

NAMES = 0x7E1548
SAVES = Path(__file__).parent / "saves"


def test_a_record_ends_its_name_and_its_nickname() -> None:
    assert record(b"AB", b"ABCDE") == b"AB\xff\xff\xff\xff\xffABCD\xff"


def test_a_name_past_the_slot_fails_the_build() -> None:
    with pytest.raises(ValueError, match="slot holds 6"):
        record(b"ABCDEFG", b"")


def test_every_french_name_fits() -> None:
    assert len(defaults(Table(str(TABLE)))) == 12 * RECORD


def test_ratix_nick_is_his_nickname_the_others_their_name() -> None:
    names = inserts()
    assert (names["ラティ"], names["ラティクス"], names["ミリー"]) == ("Raty", "Ratix", "Millie")


def test_dejap_codes_capitals_and_small_letters_apart() -> None:
    assert dejap_names()[0] == bytes([0x32, 0x42, 0x55, 0x4A, 0x59])  # Ratix, as fantasyanime_1.srm holds it


@pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")
def test_a_dejap_save_loads_with_the_french_names() -> None:
    emu = emulator("title_continue", (SAVES / "fantasyanime_1.srm").read_bytes())
    tap(emu, "A,A,A,A,A")  # load screen, last slot saved, Oui
    emu.run_frames(600)
    assert bytes(emu.read_range(NAMES, 12 * RECORD)) == defaults(Table(str(TABLE)))
