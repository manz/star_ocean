"""French dialog laid out to the window with katsuji reflow: each page's lines re-wrapped to the window's pixels.

A page is the text between two [page] codes. A line ending with [br] (a speaker, a choice) stays as written; what
follows the last one is reflowed by sentences. A line starting with [center] gets the [pos] x that centres it.
Widths are the katsuji font's advance (width + 1 px), a name tag measures as the French name it inserts, other
tags measure nothing. The window keeps room for a line's 1 px of shade each side.
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
WINDOW_WIDTH = 196 - 2  # pixels: the dispatcher peeks for a break once the pen passes $C5, less the shade
MIN_BALANCED_WIDTH = WINDOW_WIDTH * 2 // 3  # a sentence broken at spaces never balances narrower
PAGE = "[page]\n"
END = "[end]"
TAG = re.compile(r"\[[^\]]*\]")
NAME_TAG = re.compile(r"\[(?:nick|name):([^\]]*)\]")
BREAK = "[br]\n"  # ends a line kept as written (a speaker, a choice), then a plain line break
CENTER = "[center]"  # starts a line (a place name): becomes the [pos] that centres it
CENTRE_WIDTH = 208  # pixels the Japanese [pos] x values centre on: x = (208 - 12 px * glyphs) / 2


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
        return TextLayout(measure=self.measure, width=WINDOW_WIDTH, min_balanced_width=MIN_BALANCED_WIDTH)

    def page(self, text: str) -> str:
        text = re.sub(r"^ (?! )", "", text)  # a sentence split across [page]: katsuji keeps an indented line as is
        *kept, body = text.split(BREAK)
        return "".join(line + "\n" for line in kept) + self.layout.reflow(body)

    def message(self, text: str) -> str:
        """One message's XML text, `[end]` included, laid out."""
        body, end, rest = text.partition(END)
        pages = body.split(PAGE)
        laid = PAGE.join(self.page(page) if page else page for page in pages)
        return "\n".join(self.centre(line) for line in laid.split("\n")) + end + rest

    def centre(self, line: str) -> str:
        head, sep, text = line.partition(CENTER)
        if not sep:
            return line
        ink = max(self.measure(text) - 1, 0)  # the last advance's gap isn't ink
        return f"{head}[pos][0x{max(CENTRE_WIDTH - ink, 0) // 2:x}][0x0]{text}"

    def overflows(self, text: str) -> list[str]:
        """Lines of a laid-out message wider than the window. A page taller than the window's 4 lines is fine: the
        game prompts, then scrolls."""
        lines = text.partition(END)[0].replace(PAGE, "\n").split("\n")
        return [f"{self.measure(line)} px: {line[:30]!r}" for line in lines if self.measure(line) > WINDOW_WIDTH]
