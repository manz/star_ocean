"""S-DD1 streams in the base ROM. The codec (the chip's decompressor, and a compressor whose output it reads back)
lives in katsuji.codecs.sdd1; this reads a stream off the cartridge bus.
"""

from __future__ import annotations

from katsuji.codecs.sdd1 import compress, decompress_bytes

from tools.rom import Rom

__all__ = ["compress", "decompress", "decompress_bytes"]


def decompress(bus_addr: int, size: int, rom: Rom | None = None) -> tuple[bytes, int]:
    """`size` decompressed bytes of the stream at `bus_addr` in the base ROM; returns (data, compressed size)."""
    rom = rom or Rom()
    return decompress_bytes(rom.read(bus_addr, min(size * 2 + 16, 0x10000 - (bus_addr & 0xFFFF))), size)
