"""French dialog laid out to the window with katsuji reflow: each page's lines re-wrapped to the window's pixels.

A page is the text between two [page] codes. A speaker line ends with [br] and stays as written; the rest is
reflowed by sentences. Widths are the katsuji font's advance (width + 1 px), a name tag measures as the French
name it inserts, other tags measure nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from katsuji.formats import VwfFont
from katsuji.layout import TextLayout

from tools.rom import ROOT

FONT = ROOT / "build" / "gen" / "dialog_font.dat"
TABLE = ROOT / "text" / "so_fr.tbl"
WINDOW_WIDTH = 196  # pixels: the dispatcher peeks for a break once the pen passes $C5
PAGE = "[page]\n"
END = "[end]"
TAG = re.compile(r"\[[^\]]*\]")
NAME_TAG = re.compile(r"\[(?:nick|name):([^\]]*)\]")
BREAK = "[br]\n"  # ends a speaker line: kept as written, then a plain line break


def _char_widths(font: Path, table: Path) -> dict[str, int]:
    widths = VwfFont.decode(font.read_bytes()).widths
    out = {}
    for line in table.read_text(encoding="utf-8").splitlines():
        code, _, char = line.partition("=")
        out[char] = widths[int(code, 16)] + 1
    return out


@dataclass
class DialogLayout:
    names: dict[str, str]  # Japanese name in the tag -> the French name it inserts
    widths: dict[str, int] = field(default_factory=lambda: _char_widths(FONT, TABLE))

    def measure(self, line: str) -> int:
        text = NAME_TAG.sub(lambda m: self.names.get(m[1], m[1]), line)
        return sum(self.widths.get(char, 0) for char in TAG.sub("", text))

    @property
    def layout(self) -> TextLayout:
        return TextLayout(measure=self.measure, width=WINDOW_WIDTH)

    def page(self, text: str) -> str:
        text = re.sub(r"^ (?! )", "", text)  # a sentence split across [page]: katsuji keeps an indented line as is
        label, sep, body = text.partition(BREAK)
        if sep:
            return label + "\n" + self.layout.reflow(body)
        return self.layout.reflow(text)

    def message(self, text: str) -> str:
        """One message's XML text, `[end]` included, laid out."""
        body, end, rest = text.partition(END)
        pages = body.split(PAGE)
        return PAGE.join(self.page(page) if page else page for page in pages) + end + rest

    def overflows(self, text: str) -> list[str]:
        """Lines of a laid-out message wider than the window. A page taller than the window's 4 lines is fine: the
        game prompts, then scrolls."""
        lines = text.partition(END)[0].replace(PAGE, "\n").split("\n")
        return [f"{self.measure(line)} px: {line[:30]!r}" for line in lines if self.measure(line) > WINDOW_WIDTH]
