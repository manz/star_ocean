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
    0xC20669: "a93cd59d0000a901259d0200a9d6019d0400a9392e9d0600a91b1f9d0800a954019d0a00a9ffff9d0c00fa60",  # chest suffix
    0xCA7097: "a961",  # main menu HP slash: lda #0x61
    0xCA709F: "a961",
    0xCA70A7: "a961",
    0xCA70AF: "a961",
    0xCA7DFF: "a2bbeaa00202",  # save screen: ldx #EABB / ldy #0x0202
    0xCA7E21: "a2bbeaa00202",  # load screen
    0xCA700D: "a273eaa01705",  # main menu: ldx #EA73 / ldy #0x0517
    0xCA7E5A: "a273eaa01708",  # save screen
    0xCA5A95: "20fdba",  # Talents combo slot: jsr BAFD (battle16 printer)
    0xCA24DB: "a91600",  # name entry grid: last row 0x16
    0xCA88B5: "a00202",
    0xCA88DF: "a00204",  # name entry "Choix d'un nom": ldy #0x0202
    0xCA7C11: "a00101",  # Statut equipment labels: ldy #0x0101
    0xCA7D9E: "a00111",  # its favourite dish: ldy #0x1101
    0xCA6FA3: "a9048de206",  # main menu commands: lda #4 / sta 06E2 (window x)
    0xCA0280: "101048108010b810101c481c801cb81c",  # main menu cursor (x, y)
    0xCA6FC8: "a9158520",  # save greying x: lda #0x15 / sta 20
    0xCA6FD0: "a9038522",  # save greying width: lda #3 / sta 22
    0xCA06B5: "a9988522a968",  # settings button icons: lda #x / sta 22 / lda #y (x 0x98 + 8 * row)
    0xCA06C8: "a9a08522a974",
    0xCA06DB: "a9a88522a980",
    0xCA06EE: "a9b08522a98c",
    0xCA0701: "a9b88522a998",
    0xCA0714: "a9c08522a9a4",
    0xCA31FA: "a00807",  # Groupe submenu window: ldy #0x0708 (height, width)
    0xCA3276: "a00807",  # its close
    0xCA3257: "a944",  # its HDMA fill width
    0xC14797: "a9080022ca45c0",  # battle enemy name: lda #8 / jsl C045CA (blank 8 cells)
    0xC147A6: "a9080022ca45c0",  # the row above
    0xCABCAD: "a00000a624",  # 8x8 writer: ldy #0 / ldx $24
    0xCA6CD1: "a9201c0106",  # menu upload end: lda #0x20 / trb 0601
    0xCA64CD: "a278a0",  # menu font loads: ldx #0xA078
    0xCA6832: "a278a0",
    0xCA9864: "1021",  # combo description: bpl past the katakana reading
    0xCA98C9: "a953",  # its range marker: lda #'S'
    0xCA98DB: "a953",
    0xCACE50: "ad150785300a0a18653018690e8500a5008520a9098521a9058522a9028523a9038524203dd260",  # sound rect
    0xCAACA0: "20a9ac20ccac",  # menu16 copy: jsr find / jsr merge
    0xC07FD8: "03",  # header: SRAM 8 KB
}


@pytest.mark.parametrize("address", HOOKS, ids=lambda a: f"{a:06X}")
def test_hook_site_holds_the_expected_code(address: int) -> None:
    expected = bytes.fromhex(HOOKS[address].replace(" ", ""))
    assert Rom().read(address, len(expected)) == expected
