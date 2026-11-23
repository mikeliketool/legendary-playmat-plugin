"""Acceptance tests for the printing spec: mat sizes, print settings, and how inches become canvas pixels.

At Inked Gaming's default of 150 DPI with a 1/4" bleed, the canvas must be exactly the size of their templates, and
the scaled sizes must match the existing mats.
"""

import pytest
from printing_spec.consts import Mat
from printing_spec.structs import (
    CanvasBox,
    MatBox,
    PrintSettings,
    Style,
)
from printing_spec.transforms import (
    canvas_size,
    position_to_pixels,
    style_for,
    to_canvas,
    trim_offset,
)

TEMPLATE_SIZES = {Mat.STANDARD: (3675, 2175), Mat.OVERSIZE: (4275, 2175)}

MATS = [Mat.STANDARD, Mat.OVERSIZE]


def test_mats_have_their_trim_sizes_in_inches() -> None:
    assert (Mat.STANDARD.width, Mat.STANDARD.height) == (24, 14)
    assert (Mat.OVERSIZE.width, Mat.OVERSIZE.height) == (28, 14)


def test_default_settings_are_150_dpi_and_a_quarter_inch_bleed() -> None:
    settings = PrintSettings()
    assert (settings.dpi, settings.bleed) == (150, 0.25)


@pytest.mark.parametrize(("dpi", "bleed"), [(150, 0.0), (600, 0.5), (300, 0.125)])
def test_settings_inside_the_limits_are_accepted(dpi: int, bleed: float) -> None:
    settings = PrintSettings(dpi=dpi, bleed=bleed)
    assert (settings.dpi, settings.bleed) == (dpi, bleed)


@pytest.mark.parametrize(("dpi", "bleed"), [(149, 0.25), (601, 0.25), (150, -0.01), (150, 0.51)])
def test_settings_outside_the_limits_are_rejected(dpi: int, bleed: float) -> None:
    with pytest.raises(ValueError):
        PrintSettings(dpi=dpi, bleed=bleed)


def test_canvas_size_rounds_halves_up() -> None:
    # 24.5 x 301 = 7374.5 and 14.5 x 301 = 4364.5. Python's round() would give 7374 and 4364.
    assert canvas_size(Mat.STANDARD, PrintSettings(dpi=301, bleed=0.25)) == (7375, 4365)


def test_trim_offset_rounds_down() -> None:
    assert trim_offset(PrintSettings(dpi=150, bleed=0.25)) == 37
    assert trim_offset(PrintSettings(dpi=301, bleed=0.25)) == 75
    assert trim_offset(PrintSettings(dpi=150, bleed=0.0)) == 0


def test_positions_are_measured_from_the_trim_and_round_halves_up() -> None:
    # 75 px of bleed, plus 0.5 x 301 = 150.5 rounded up to 151.
    assert position_to_pixels(0.5, PrintSettings(dpi=301, bleed=0.25)) == 226


def test_box_size_comes_from_its_rounded_edges() -> None:
    # Edges: 75 + 151 = 226 and 75 + 903 = 978, so the width is 752, not round(2.5 x 301 = 752.5).
    box = MatBox(left=0.5, top=0.5, width=2.5, height=3.5)
    assert to_canvas(box, PrintSettings(dpi=301, bleed=0.25)) == CanvasBox(x=226, y=226, width=752, height=1053)


@pytest.mark.parametrize("mat", MATS)
def test_default_canvas_matches_inked_gamings_templates(mat: Mat) -> None:
    assert canvas_size(mat, PrintSettings()) == TEMPLATE_SIZES[mat]


@pytest.mark.parametrize("mat", MATS)
def test_default_trim_is_37_px_in_at_left_and_top_and_38_px_at_right_and_bottom(mat: Mat) -> None:
    settings = PrintSettings()
    width, height = canvas_size(mat, settings)
    assert trim_offset(settings) == 37
    assert width - position_to_pixels(mat.width, settings) == 38
    assert height - position_to_pixels(mat.height, settings) == 38


@pytest.mark.parametrize(("mat", "expected"), [(Mat.STANDARD, (7350, 4350)), (Mat.OVERSIZE, (8550, 4350))])
def test_canvas_at_300_dpi(mat: Mat, expected: tuple[int, int]) -> None:
    assert canvas_size(mat, PrintSettings(dpi=300, bleed=0.25)) == expected


def test_sizes_at_150_dpi_match_the_existing_mats() -> None:
    assert style_for(PrintSettings()) == Style(
        label_font_size=54, title_font_size=150, outline_thickness=3, line_width=3, corner_radius=30
    )


def test_sizes_scale_with_dpi_but_not_with_bleed() -> None:
    expected = Style(label_font_size=108, title_font_size=300, outline_thickness=6, line_width=6, corner_radius=60)
    assert style_for(PrintSettings(dpi=300, bleed=0.25)) == expected
    assert style_for(PrintSettings(dpi=300, bleed=0.0)) == expected
