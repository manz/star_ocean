"""Decoder for the C0:4C53 container (0x81 LZSS, 0x83 LZSS + RLE, anything else raw)."""

from __future__ import annotations

from collections.abc import Callable

from katsuji.codecs.lzss import Lzss

Reader = Callable[[int, int], bytes]
HEADER_SIZE = 9
LZSS = Lzss(window=0xFFF)  # 0x81; tools/encode_text.py packs with the same format


def decode(read: Reader, header: int) -> tuple[bytes, int]:
    """Decode the container at bus address ``header``. Returns ``(data, input_size)``: the bytes the container owns.
    A raw one owns ``rawlen`` bytes, yet the game copies one more: the first byte of whatever follows."""
    head = read(header, HEADER_SIZE)
    kind = head[0]
    if kind not in (0x81, 0x83):
        raw = head[5] | head[6] << 8
        return read(header + HEADER_SIZE, raw + 1), HEADER_SIZE + raw
    size = head[1] | head[2] << 8
    if kind == 0x81:
        return LZSS.decompress(read(header + HEADER_SIZE, size), head[5] | head[6] << 8)[0], HEADER_SIZE + size
    return _lzss_rle(read(header + HEADER_SIZE, size + 3), size), HEADER_SIZE + size


def _lzss_rle(src: bytes, size: int) -> bytes:
    """0x83: the 0x81 LZSS plus run references (b1 >= 0xF0), which katsuji's Lzss lacks."""
    out = bytearray()
    p = flags = bits = 0
    while p < size:
        if bits == 0:
            flags, bits = src[p], 8
            p += 1
            if p >= size:
                break
        literal = flags & 1
        flags >>= 1
        bits -= 1
        if literal:
            out.append(src[p])
            p += 1
            continue
        b0, b1 = src[p], src[p + 1]
        if b1 >= 0xF0:
            if b1 & 0x0F:
                out += bytes([b0]) * ((b1 & 0x0F) + 3)
                p += 2
            else:
                out += bytes([src[p + 2]]) * (b0 + 0x13)
                p += 3
            continue
        dist = b0 | (b1 & 0x0F) << 8
        for _ in range((b1 >> 4) + 3):
            out.append(out[-dist] if 0 < dist <= len(out) else 0)
        p += 2
    return bytes(out)
