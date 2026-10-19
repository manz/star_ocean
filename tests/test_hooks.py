"""Every patch hook overwrites the base ROM bytes it was written against."""

from __future__ import annotations

import pytest

from tools.rom import DEFAULT_ROM, Rom

pytestmark = pytest.mark.skipif(not DEFAULT_ROM.exists(), reason="base ROM not present")

# hook address -> the instructions it replaces
HOOKS = {
    0xC61137: "22534cc0",  # scene_load_script: jsl unpack
    0xC21C47: "bd73b81869 73b88dd503",  # message select (event op)
    0xC21CAC: "bd73b81869 73b88dd503",  # text_message_select
    0xC23F14: "0aaabf213fc2a8fa20513f7a60",  # text_insert_string, ids < 0x18
    0xC263B4: "b900008531",  # glyph fetch: first lda 0,y / sta $31
    0xC265B9: "a5d918690c65db85d9",  # pen advance
    0xC2416A: "c91100",  # line measure: 17 glyphs
    0xC24122: "a901",  # letter spacing 1 on short lines
    0xC07FD8: "03",  # header: SRAM 8 KB
}


@pytest.mark.parametrize("address", HOOKS, ids=lambda a: f"{a:06X}")
def test_hook_site_holds_the_expected_code(address: int) -> None:
    expected = bytes.fromhex(HOOKS[address].replace(" ", ""))
    assert Rom().read(address, len(expected)) == expected
