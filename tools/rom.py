"""The base ROM read through the a816 bus `a816.toml` declares (S-DD1 power-on MMC pages)."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path

from a816.config import load_a816_toml
from a816.cpu.mapping import Bus
from a816.mappers import map_on_bus

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROM = ROOT / "Star Ocean (Japan).sfc"


class Rom:
    def __init__(self, path: Path = DEFAULT_ROM, config: Path = ROOT / "a816.toml") -> None:
        self.data = path.read_bytes()
        self._config = config

    @cached_property
    def bus(self) -> Bus:
        cfg = load_a816_toml(self._config)
        if cfg is None:
            raise FileNotFoundError(self._config)
        bus = Bus("star_ocean")
        for mapping in cfg.bus_map:
            map_on_bus(bus, mapping)
        return bus

    def offset(self, bus_addr: int) -> int:
        physical = self.bus.get_address(bus_addr).physical
        if physical is None:
            raise ValueError(f"${bus_addr:06X} is not ROM")
        return physical

    def read(self, bus_addr: int, size: int) -> bytes:
        off = self.offset(bus_addr)
        return self.data[off : off + size]
