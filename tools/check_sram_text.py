"""Run the patch's SRAM text routines on every scene in kintsuki: each block the patched scene table points at
unpacks to $70:0000 byte for byte and each message selected lands at $7E:B873 as the block has it (the Japanese
blocks of the translated scenes hold other data now: tools/encode_menus.py text16).

Own process: kintsuki allows one emulator per process.
"""

from __future__ import annotations

import sys

from kintsuki import CpuState, Emu

from tools.dialog import SCENES, messages, scene_block, scene_text_ptr
from tools.patch import build
from tools.rom import Rom

STUB = 0x7FF000  # WRAM the stub runs from; the game is stopped
TEXT_BUFFER = 0x7EB873
# sei; rep #$30; lda #0; tcd; sep #$20; lda #0; sta $004200 (no NMI); lda #$7E; pha; plb; rep #$10
PROLOGUE = bytes.fromhex("78c230a900005be220a9008f004200a97e48abc210")


def _call(emu: Emu, target: int, *, a8: int = 0, x16: int = 0, y16: int = 0, m16: bool = False) -> CpuState:
    """`jsl target` as the game makes it: D = 0, DB = $7E, X16, A 8-bit (or 16 with `m16`), A, X and Y given."""
    regs = bytes([0xA0, y16 & 0xFF, y16 >> 8, 0xA2, x16 & 0xFF, x16 >> 8, 0xA9, a8]) + (b"\xc2\x20" if m16 else b"")
    jsl = bytes([0x22, target & 0xFF, target >> 8 & 0xFF, target >> 16])
    state: CpuState = emu.run_asm(PROLOGUE + regs + jsl, load_addr=STUB)
    if state.pc & 0xFFFFFF != emu.EXIT_PC:
        raise RuntimeError(f"stub for {target:06X} did not return")
    return state


def check() -> list[str]:
    patch = build()
    rom = Rom().with_ips(patch.ips)
    unpack, select = patch.symbols["text_unpack_sram"], patch.symbols["text_select_message"]
    sram_text, sram_text_size = patch.symbols["sram_text"], patch.symbols["sram_text_size"]
    emu = Emu()
    emu.load_rom(str(patch.rom))
    emu.run_frames(300)
    # run_frames can leave the core suspended mid-instruction; registers set then mix with the pending fetch
    # (the first stub starts at a garbage address). One step() lands on an instruction boundary; every stub
    # then stops on one (its exit).
    emu.step()
    errors = []
    for scene in range(1, SCENES + 1):
        ptr, block = scene_text_ptr(rom, scene), scene_block(rom, scene)
        state = _call(emu, unpack, a8=ptr >> 16, y16=ptr & 0xFFFF)
        if bytes(emu.read_range(sram_text, len(block))) != block or emu.read16(sram_text_size) != len(block):
            size = emu.read16(sram_text_size)
            errors.append(f"scene {scene}: unpack ({size} bytes, expected {len(block)}, pc {state.pc:06X})")
            continue
        for index, message in enumerate(messages(block)):
            state = _call(emu, select, x16=index * 2, m16=True)
            if bytes(emu.read_range(TEXT_BUFFER, len(message))) != message or state.x != index * 2:
                errors.append(f"scene {scene} message {index}: select")
                break
    return errors


def main() -> None:
    errors = check()
    print("\n".join(errors) or f"{SCENES} scenes ok")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
