"""Battle text: the C0 copies of the 16x16 readers take the one-byte strings (src/menu/text16.s)."""

from __future__ import annotations

from tests.screens import IPS, emulator
from tools.rom import Rom

APU_WAIT = range(0xC00331, 0xC0033C)  # the IRQ's sound handshake: stuck there once direct page is overwritten


def test_item_found_message_does_not_hang_the_battle() -> None:
    emu = emulator("battle_text")  # just before "Myrtille a été obtenu !"
    emu.run_frames(700)
    assert emu.get_state().pc & 0xFFFFFF not in APU_WAIT


def test_the_uncalled_c0_reader_traps_a_found_id() -> None:
    rom = Rom().with_ips(IPS)
    assert (rom.read(0xC04B27, 2), rom.read(0xC04B30, 2)) == (b"\xf0\x07", b"\x00\x4b")  # beq to the hit: brk #$4B
