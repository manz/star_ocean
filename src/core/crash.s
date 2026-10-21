"""
Crash stop. The game's BRK / COP / abort handler (`00:FEA9`, vectors at `C0:7FE4`) turns on interlace, forces
blank and spins: the frozen screen looks like a soft lock and the emulator keeps running. `stp` halts the CPU
where it is, which kintsuki reports (`CpuState.stp`, `run_until_stp`).
"""

; 00:FEA9, the handler's first byte, through the C0 window.
.alloc at 0xC07EA9 size 1 {
    stp
}
