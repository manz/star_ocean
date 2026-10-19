"""S-DD1 codec in Python: the chip's decompressor, and a compressor whose output it reads back.

The stream (Andreas Naive's description, as ares implements it): byte 0's top nibble is the header (bits 7-6
bitplane layout, bits 5-4 context bits), then Golomb codewords, MSB first. Eight bit generators (code number
k = 0-7) each play a run: codeword `0` = 2^k MPS, `1` + k bits = n MPS then one LPS. A probability estimation
module keeps 32 contexts (state + MPS), the context model picks the context from the bitplane's previous bits,
the output logic interleaves bitplanes into bytes.

The compressor replays the same model over the known bits: a generator asks for a codeword where the decoder
would read one, and the codeword is written once its run is over, so the codewords land in the order the decoder
reads them. Every one of the 16 headers is tried, the shortest stream kept.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from tools.rom import Rom


def _run_count(k: int, bits: int) -> int:
    """GCD: MPS before the LPS for code number `k` and the `k` bits read: the bits reversed, complemented."""
    return ~int(f"{bits:0{k}b}"[::-1] or "0", 2) & ((1 << k) - 1)


# PEM states: (code number, next if MPS, next if LPS).
EVOLUTION = (
    (0, 25, 25), (0, 2, 1), (0, 3, 1), (0, 4, 2), (0, 5, 3), (1, 6, 4), (1, 7, 5), (1, 8, 6), (1, 9, 7),
    (2, 10, 8), (2, 11, 9), (2, 12, 10), (2, 13, 11), (3, 14, 12), (3, 15, 13), (3, 16, 14), (3, 17, 15),
    (4, 18, 16), (4, 19, 17), (5, 20, 18), (5, 21, 19), (6, 22, 20), (6, 23, 21), (7, 24, 22), (7, 24, 23),
    (0, 26, 1), (1, 27, 2), (2, 28, 4), (3, 29, 8), (4, 30, 12), (5, 31, 16), (6, 32, 18), (7, 24, 22),
)  # fmt: skip
HEADERS = tuple(planes << 6 | context << 4 for planes in range(4) for context in range(4))
# k -> run length n -> the k bits that decode to n
RUN_BITS = tuple({_run_count(k, v): v for v in range(1 << k)} for k in range(8))


@dataclass
class _Context:
    """Context model + probability estimation: which generator plays the next bit, and its MPS."""

    header: int
    plane: int = 0
    bit_number: int = 0
    history: list[int] = field(default_factory=lambda: [0] * 8)
    status: list[int] = field(default_factory=lambda: [0] * 32)
    mps: list[int] = field(default_factory=lambda: [0] * 32)

    def __post_init__(self) -> None:
        self.plane = {0x00: 1, 0x40: 7, 0x80: 3}.get(self.header & 0xC0, 0)

    def next_context(self) -> int:
        layout, first = self.header & 0xC0, not (self.bit_number & 0x7F)
        if layout == 0xC0:
            self.plane = self.bit_number & 7
        else:
            self.plane ^= 1
            if layout == 0x40 and first:
                self.plane = (self.plane + 2) & 7
            elif layout == 0x80 and first:
                self.plane ^= 2
        bits = self.history[self.plane]
        context = (self.plane & 1) << 4
        match self.header & 0x30:
            case 0x00:
                return context | (bits & 0x1C0) >> 5 | bits & 1
            case 0x10:
                return context | (bits & 0x180) >> 5 | bits & 1
            case 0x20:
                return context | (bits & 0x0C0) >> 5 | bits & 1
            case _:
                return context | (bits & 0x180) >> 5 | bits & 3

    def code(self, context: int) -> int:
        return EVOLUTION[self.status[context]][0]

    def end_run(self, context: int, lps: int) -> None:
        state = EVOLUTION[self.status[context]]
        if lps:
            if self.status[context] < 2:
                self.mps[context] ^= 1
            self.status[context] = state[2]
        else:
            self.status[context] = state[1]

    def push(self, bit: int) -> None:
        self.history[self.plane] = (self.history[self.plane] << 1 | bit) & 0xFFFF
        self.bit_number += 1


def _bit_order(header: int, size: int) -> Iterator[tuple[int, int]]:
    """(byte index, bit mask) in the order the output logic asks the context model for bits."""
    if header & 0xC0 == 0xC0:
        for i in range(size):
            for b in range(8):
                yield i, 1 << b
        return
    for i in range(0, size, 2):
        for b in range(7, -1, -1):
            yield i, 1 << b
            yield i + 1, 1 << b


class _Reader:
    def __init__(self, src: bytes) -> None:
        self.src, self.offset, self.bit_count = src, 0, 4

    def _byte(self, i: int) -> int:
        return self.src[i] if i < len(self.src) else 0

    def codeword(self, k: int) -> int:
        word = self._byte(self.offset) << self.bit_count & 0xFF
        self.bit_count += 1
        if word & 0x80:
            word |= self._byte(self.offset + 1) >> (9 - self.bit_count)
            self.bit_count += k
        if self.bit_count & 8:
            self.offset += 1
            self.bit_count &= 7
        return word


def decompress_bytes(src: bytes, size: int) -> tuple[bytes, int]:
    """`size` bytes out of the stream `src`; returns (data, bytes of `src` read)."""
    reader, model = _Reader(src), _Context(src[0] & 0xF0)
    runs = [[0, 0] for _ in range(8)]  # per generator: MPS left, LPS pending
    out = bytearray(size + 1)
    for index, mask in _bit_order(model.header, size):
        context = model.next_context()
        k = model.code(context)
        run = runs[k]
        if not (run[0] or run[1]):
            word = reader.codeword(k)
            run[:] = [_run_count(k, word >> (k ^ 7) & ((1 << k) - 1)), 1] if word & 0x80 else [1 << k, 0]
        if run[0]:
            lps, run[0] = 0, run[0] - 1
        else:
            lps, run[1] = 1, 0
        bit = lps ^ model.mps[context]  # the MPS before this run's update
        if not (run[0] or run[1]):
            model.end_run(context, lps)
        model.push(bit)
        if bit:
            out[index] |= mask
    return bytes(out[:size]), reader.offset + (reader.bit_count > 0)


def _encode(data: bytes, header: int) -> bytes:
    model = _Context(header)
    words: list[tuple[int, int] | None] = []  # (value, bit length) in the order the decoder reads them
    open_runs: list[tuple[int, int] | None] = [None] * 8  # per generator: (word slot, MPS so far)
    for index, mask in _bit_order(header, len(data)):
        bit = 1 if index < len(data) and data[index] & mask else 0
        context = model.next_context()
        k = model.code(context)
        lps = bit ^ model.mps[context]
        slot, count = open_runs[k] or (len(words), 0)
        if open_runs[k] is None:
            words.append(None)
        ended = True
        if lps:
            words[slot] = (1 << k | RUN_BITS[k][count], k + 1)
        elif count + 1 == 1 << k:
            words[slot] = (0, 1)
        else:
            ended = False
        open_runs[k] = None if ended else (slot, count + 1)
        if ended:
            model.end_run(context, lps)
        model.push(bit)
    for run in open_runs:
        if run is not None:
            words[run[0]] = (0, 1)  # a full MPS run: the decoder stops before it runs out
    return _pack(header, words)


def _pack(header: int, words: list[tuple[int, int] | None]) -> bytes:
    acc, length = header >> 4, 4
    for word in words:
        assert word is not None
        value, bits = word
        acc, length = acc << bits | value, length + bits
    pad = -length % 8
    return (acc << pad).to_bytes((length + pad) // 8, "big")


def compress(data: bytes) -> bytes:
    """The shortest stream `decompress_bytes` turns back into `data`."""
    return min((_encode(data, header) for header in HEADERS), key=len)


def decompress(bus_addr: int, size: int, rom: Rom | None = None) -> tuple[bytes, int]:
    """`size` decompressed bytes of the stream at `bus_addr` in the base ROM; returns (data, compressed size)."""
    rom = rom or Rom()
    return decompress_bytes(rom.read(bus_addr, min(size * 2 + 16, 0x10000 - (bus_addr & 0xFFFF))), size)
