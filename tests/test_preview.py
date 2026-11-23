"""The dialog preview (tools/preview.py): messages laid out as the reflow does, judged in a window that scrolls."""

from __future__ import annotations

import pytest

pytest.importorskip("katsuji.preview", reason="katsuji with the preview")

from katsuji.script.sn import Message

from tools.preview import Dialog, game
from tools.reflow import FONT, WINDOW_WIDTH, DialogLayout

pytestmark = pytest.mark.skipif(not FONT.exists(), reason="font not built (python -m tools.patch)")

MESSAGE = Message("scene_05", "0", "", {})
LONG = "Nous n'avons pas tous sauté en même temps, il est probable qu'une grande distance nous sépare."


@pytest.fixture(scope="module")
def dialog() -> Dialog:
    return Dialog(DialogLayout({"ドーン": "Dorn"}))


def test_pages_are_windows(dialog: Dialog) -> None:
    assert len(dialog.lay(MESSAGE, "Un[page]\nDeux[page]\n[end]")) == 2


def test_the_end_is_dropped(dialog: Dialog) -> None:
    assert dialog.lay(MESSAGE, "Un[end][0xff]") == [["Un"]]


def test_a_long_page_scrolls_not_faults(dialog: Dialog) -> None:
    laid = dialog.lay(MESSAGE, " ".join([LONG] * 3) + "[end]")
    judge = dialog.frame(MESSAGE).judge
    assert (judge.faults(laid), judge.flaws(laid).scrolls > 0) == ([], True)


def test_a_name_draws_as_its_name(dialog: Dialog) -> None:
    assert dialog.draw("[nick:ドーン]", "").shape == dialog.draw("Dorn", "").shape


def test_a_pos_is_room_left_of_the_line(dialog: Dialog) -> None:
    assert dialog.draw("[pos][0x10][0x0]A", "").shape[1] == dialog.draw("A", "").shape[1] + 0x10


def test_an_empty_line_draws_nothing(dialog: Dialog) -> None:
    assert dialog.draw("[br]", "").shape[1] == 0


def test_a_window_is_the_dialog_window(dialog: Dialog) -> None:
    assert dialog.frame(MESSAGE).judge.window.width == WINDOW_WIDTH


def test_the_game_places_a_scene_by_its_banner() -> None:
    assert any(" · クラトスの町" in scene.title for scene in game().scenes())
