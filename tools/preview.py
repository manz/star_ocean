"""The French script in the browser, laid out, drawn and judged as it is typed (`katsuji preview`).

    uv run katsuji preview tools.preview:game   # then http://127.0.0.1:8732 (needs build/gen fonts: tools.patch)

The script side is katsuji's `ScriptGame`: the `sn:script` files of `text/fr` (originals in `text/jp`), placed by
`text/scenes.xml` (`tools.scenes`: a scene per scene file, titled by its place banner, its messages by trigger);
saving writes the message's file. This module gives how a message is set and drawn: laid out as `tools.reflow`
lays it, each page a window of 4 lines that scrolls past its 4th (the game prompts, then scrolls: no line overflows
a page), drawn in the dialog font, a name tag as the French name it inserts, a `[pos]` as the room left of the line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property

import numpy as np
from katsuji.dialog import Window
from katsuji.flow import Judge, Laid
from katsuji.formats import VwfFont
from katsuji.png import Pixels
from katsuji.preview import Frame
from katsuji.preview.script_game import ScriptGame
from katsuji.render import render
from katsuji.script import Table
from katsuji.script.sn import Message

from tools.party_names import inserts
from tools.reflow import END, FONT, NAME_TAG, PAGE, TABLE, TAG, WINDOW_WIDTH, DialogLayout
from tools.scenes import SCENES, TEXT

LINES = 4  # a window's lines before it scrolls
GAP = 1  # px between glyphs: a glyph's advance is its width + 1
POS = re.compile(r"\[pos\]\[0x([0-9a-fA-F]+)\]\[0x[0-9a-fA-F]+\]")


@dataclass
class Dialog:
    """How each message of the French script is set and drawn."""

    layout: DialogLayout = field(default_factory=lambda: DialogLayout(inserts()))

    @cached_property
    def font(self) -> VwfFont:
        return VwfFont.decode(FONT.read_bytes())

    @cached_property
    def table(self) -> Table:
        return Table(str(TABLE))

    @cached_property
    def dialog_frame(self) -> Frame:
        judge = Judge(self.layout.layout, Window(WINDOW_WIDTH, LINES, scrolls=True))
        return Frame(judge, self.font.height, self.draw)

    def frame(self, message: Message) -> Frame:
        return self.dialog_frame

    def lay(self, message: Message, text: str) -> Laid:
        """The message as the game lays it out: its pages, each its lines, `[end]` and what follows it dropped."""
        laid = self.layout.message(text).partition(END)[0]
        return [page.split("\n") for page in laid.split(PAGE) if page.strip()]

    def draw(self, line: str, before: str) -> Pixels:
        """A line in the dialog font: a `[pos]` as blank room left of it, a name tag as its name, other tags out."""
        found = POS.search(line)
        left = int(found[1], 16) if found else 0
        text = TAG.sub("", NAME_TAG.sub(lambda match: self.layout.names.get(match[1], match[1]), line))
        drawn = render(self.font, list(self.table.to_bytes(text)), gap=GAP) if text else self._blank(0)
        return np.concatenate([self._blank(left), drawn], axis=1)

    def _blank(self, width: int) -> Pixels:
        return np.zeros((self.font.height, width), dtype=np.uint8)


def game() -> ScriptGame:
    """`katsuji preview tools.preview:game`."""
    dialog = Dialog()
    return ScriptGame(TEXT / "fr", dialog.frame, dialog.lay, TEXT / "jp", SCENES)
