"""Battle text: the C0 copies of the 16x16 readers take the one-byte strings (src/menu/text16.s)."""

from __future__ import annotations

from tests.screens import emulator

APU_WAIT = range(0xC00331, 0xC0033C)  # the IRQ's sound handshake: stuck there once direct page is overwritten


def test_item_found_message_does_not_hang_the_battle() -> None:
    emu = emulator("battle_text")  # just before "Myrtille a été obtenu !"
    emu.run_frames(700)
    assert emu.get_state().pc & 0xFFFFFF not in APU_WAIT
