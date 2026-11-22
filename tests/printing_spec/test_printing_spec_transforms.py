"""Tests for printing_spec.transforms beyond the acceptance tests: floating-point edge cases and rounding."""

import pytest
from printing_spec.consts import Mat
from printing_spec.structs import PrintSettings, Style
from printing_spec.transforms import (
    canvas_size,
    position_to_pixels,
    style_for,
    trim_offset,
)

# Inches typed as decimals aren't exact in binary floating point, so their products can land just below a whole or
# half pixel. The rule must still treat them as the whole or half pixel they are on paper.


@pytest.mark.parametrize(("dpi", "bleed", "expected"), [(200, 0.29, 58), (180, 0.35, 63)])
def test_trim_offset_is_not_shifted_by_floating_point_error(dpi: int, bleed: float, expected: int) -> None:
    # 0.29 x 200 is 57.99999999999999 in floating point.
    assert trim_offset(PrintSettings(dpi=dpi, bleed=bleed)) == expected


def test_half_pixel_positions_round_up_despite_floating_point_error() -> None:
    # 0.41 x 150 is 61.49999999999999 in floating point, but 61.5 on paper, which rounds up to 62.
    assert position_to_pixels(0.41, PrintSettings()) == 37 + 62


def test_zero_bleed_makes_the_canvas_the_trim_size() -> None:
    settings = PrintSettings(dpi=150, bleed=0.0)
    assert canvas_size(Mat.STANDARD, settings) == (3600, 2100)
    assert trim_offset(settings) == 0


def test_scaled_sizes_round_halves_up() -> None:
    # At 225 DPI the old 3 px outline is 4.5 px, which rounds up to 5. Python's round() would give 4.
    assert style_for(PrintSettings(dpi=225)) == Style(
        label_font_size=81, title_font_size=225, outline_thickness=5, line_width=5, corner_radius=45
    )
