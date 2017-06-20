#!/usr/bin/env python

from a816.cpu.cpu_65c816 import RomType
from a816.program import Program
from a816.writers import IPSWriter


def build_assembly(input, writer):
    asm = Program()
    asm.resolver.rom_type = RomType.high_rom
    asm.assemble_with_emitter(input, writer)


if __name__ == '__main__':
    with open('so.ips', 'wb') as f:
        writer = IPSWriter(f)
        writer.begin()
        build_assembly('so.s', writer)
        writer.end()
