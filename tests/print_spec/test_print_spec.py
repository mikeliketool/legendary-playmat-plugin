"""Tests for print_spec.model beyond the acceptance tests: floating-point edge cases and settings errors."""

import math

import pytest
from print_spec.model import (
    Mat,
    PrintSettings,
    Style,
    UnknownCellError,
    canvas_size,
    layout_for,
    position_to_pixels,
    style_for,
    trim_offset,
)

LAYOUT_CHOICES = [(Mat.STANDARD, False), (Mat.OVERSIZE, False), (Mat.OVERSIZE, True)]


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


# Settings errors say what's allowed.


@pytest.mark.parametrize("dpi", [149, 601])
def test_dpi_error_gives_the_allowed_range(dpi: int) -> None:
    with pytest.raises(ValueError, match=r"DPI must be between 150 and 600"):
        PrintSettings(dpi=dpi)


@pytest.mark.parametrize("bleed", [-0.01, 0.51, math.nan])
def test_bleed_error_gives_the_allowed_range(bleed: float) -> None:
    with pytest.raises(ValueError, match=r"Bleed must be between 0 and 0\.5 inches"):
        PrintSettings(bleed=bleed)


def test_extra_cell_error_says_which_mat_has_one() -> None:
    with pytest.raises(ValueError, match="Only the 28x14 mat has an extra cell"):
        layout_for(Mat.STANDARD, include_extra_cell=True)


def test_unknown_cell_error_is_a_key_error_with_a_plain_message() -> None:
    # str() of a plain KeyError wraps its message in quotes, which a user shouldn't see.
    with pytest.raises(UnknownCellError) as error:
        layout_for(Mat.STANDARD).cell("extra")
    assert isinstance(error.value, KeyError)
    assert str(error.value) == "No cell with key 'extra' in this 24x14 layout."


# How the parts of a layout fit together.


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_each_card_sits_directly_under_its_label(mat: Mat, extra: bool) -> None:
    for cell in layout_for(mat, include_extra_cell=extra).cells:
        assert cell.card.left == cell.label_box.left, cell.key
        assert cell.card.width == cell.label_box.width, cell.key
        assert cell.card.top == pytest.approx(cell.label_box.bottom), cell.key


def test_scaled_sizes_round_halves_up() -> None:
    # At 225 DPI the old 3 px outline is 4.5 px, which rounds up to 5. Python's round() would give 4.
    assert style_for(PrintSettings(dpi=225)) == Style(
        label_font_size=81, title_font_size=225, outline_thickness=5, line_width=5, corner_radius=45
    )
