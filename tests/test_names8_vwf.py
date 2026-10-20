"""The names8 strips the 8x8 VWF uploads."""

from __future__ import annotations

from tools.names8_vwf import MAX_TILES, strip


def test_a_strip_is_whole_2bpp_tiles() -> None:
    data = strip("Myrtille")
    assert data is not None
    assert len(data) % 16 == 0


def test_a_proportional_name_takes_fewer_cells_than_letters() -> None:
    data = strip("AppelLapin")
    assert data is not None
    assert len(data) // 16 < len("AppelLapin")


def test_an_uppercase_accent_draws_its_base_letter() -> None:
    assert strip("BicÉtude") == strip("BicEtude")


def test_a_name_wider_than_the_field_is_left_to_the_game() -> None:
    assert strip("W" * (MAX_TILES * 2)) is None


def test_a_character_the_font_lacks_is_left_to_the_game() -> None:
    assert strip("Épée♪") is None
