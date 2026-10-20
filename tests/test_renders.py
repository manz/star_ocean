"""The tracked narration / cutscene renders: current with their inputs, and copied into build/gen without the fonts."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import renders


def test_tracked_renders_match_their_inputs() -> None:
    assert (renders.RENDERS / renders.STAMP).read_text() == renders.stamp()


def test_without_fonts_the_tracked_renders_are_copied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(renders, "fonts_present", lambda: False)
    renders.build(tmp_path)
    assert [p.name for p in renders.outputs(tmp_path)] == [p.name for p in renders.outputs(renders.RENDERS)]


def test_stale_renders_fail_the_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(renders, "fonts_present", lambda: False)
    (tmp_path / "renders").mkdir()
    (tmp_path / "renders" / renders.STAMP).write_text("old\n")
    with pytest.raises(RuntimeError, match="older than"):
        renders.build(tmp_path / "gen", tmp_path / "renders")
