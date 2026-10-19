"""Dialog layout: pages re-wrapped to the window's pixels, speaker labels and tags kept."""

from __future__ import annotations

import pytest

from tools.reflow import FONT, WINDOW_WIDTH, DialogLayout

pytestmark = pytest.mark.skipif(not FONT.exists(), reason="font not built (python -m tools.patch)")

LONG = "Nous n'avons pas tous sauté en même temps, il est probable qu'une grande distance nous sépare."


@pytest.fixture(scope="module")
def layout() -> DialogLayout:
    return DialogLayout({"ドーン": "Dorn"})


def test_name_tag_measures_as_french_name(layout: DialogLayout) -> None:
    assert layout.measure("[nick:ドーン]") == layout.measure("Dorn")


def test_other_tags_measure_nothing(layout: DialogLayout) -> None:
    assert layout.measure("[color][0x4]Dorn[color][0x2]") == layout.measure("Dorn")


def test_long_page_fits_window(layout: DialogLayout) -> None:
    out = layout.message(f"[nick:ドーン]\n{LONG}[page]\n[end]")
    assert not layout.overflows(out)


def test_speaker_label_stays_alone(layout: DialogLayout) -> None:
    assert layout.page(f"[nick:ドーン]\n{LONG}").split("\n")[0] == "[nick:ドーン]"


def test_tags_and_end_kept(layout: DialogLayout) -> None:
    out = layout.message(f"[color][0x4]{LONG}[page]\n[end]")
    assert (out.startswith("[color][0x4]"), out.endswith("[page]\n[end]")) == (True, True)


def test_stray_leading_space_dropped(layout: DialogLayout) -> None:
    assert layout.page(" poussant au Mt Métox, je pourrais être sauvé... " * 2)[0] != " "


def test_overflow_reports_wide_line(layout: DialogLayout) -> None:
    assert layout.overflows("M" * WINDOW_WIDTH + "[end]")
