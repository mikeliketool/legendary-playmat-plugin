"""Printing spec rules for a Marvel Legendary playmat: the inches-to-pixels rule and the sizes that scale with DPI.

Pure Python with no GIMP code, so it can be tested on its own. Positions are in inches from the top-left corner of
the trim (the finished mat's edge), and only become pixels at drawing time.
"""

import math

from printing_spec.consts import (
    CORNER_RADIUS_INCHES,
    LABEL_FONT_INCHES,
    LINE_WIDTH_INCHES,
    OUTLINE_THICKNESS_INCHES,
    PIXEL_PRECISION,
    TITLE_FONT_INCHES,
    Mat,
)
from printing_spec.structs import CanvasBox, MatBox, PrintSettings, Style


def canvas_size(mat: Mat, settings: PrintSettings) -> tuple[int, int]:
    """Canvas size in pixels, bleed included: round((trim + 2 x bleed) x DPI), halves rounded up.

    Args:
        mat: The mat size.
        settings: The DPI and bleed.

    Returns:
        The canvas (width, height) in pixels.
    """
    width = _round_half_up((mat.width + 2 * settings.bleed) * settings.dpi)
    height = _round_half_up((mat.height + 2 * settings.bleed) * settings.dpi)
    return width, height


def trim_offset(settings: PrintSettings) -> int:
    """Pixels from the canvas's left or top edge to the trim: floor(bleed x DPI).

    The right and bottom bleed get what's left of the canvas, so they can be a pixel or two wider.

    Args:
        settings: The DPI and bleed.

    Returns:
        The trim's offset in pixels from the canvas's left edge, which is also its offset from the top edge.
    """
    return math.floor(round(settings.bleed * settings.dpi, PIXEL_PRECISION))


def position_to_pixels(inches: float, settings: PrintSettings) -> int:
    """Canvas pixel for a position in inches from the trim: trim_offset + round(inches x DPI), halves rounded up.

    Args:
        inches: A distance from the trim's left edge (for x) or top edge (for y).
        settings: The DPI and bleed.

    Returns:
        The pixel's x or y on the canvas.
    """
    return trim_offset(settings) + _round_half_up(inches * settings.dpi)


def to_canvas(box: MatBox, settings: PrintSettings) -> CanvasBox:
    """Convert to canvas pixels: each edge goes through position_to_pixels, and the size comes from those edges.

    Args:
        box: The box in inches from the trim.
        settings: The DPI and bleed of the canvas.

    Returns:
        The box in canvas pixels, bleed included.
    """
    x = position_to_pixels(box.left, settings)
    y = position_to_pixels(box.top, settings)
    right = position_to_pixels(box.right, settings)
    bottom = position_to_pixels(box.bottom, settings)
    return CanvasBox(x, y, right - x, bottom - y)


def style_for(settings: PrintSettings) -> Style:
    """Font sizes, outline thickness, line width, and corner radius for these settings.

    Args:
        settings: The DPI and bleed. Only the DPI changes the sizes.

    Returns:
        The sizes in pixels. At 150 DPI they're the old plugin's sizes.
    """
    dpi = settings.dpi
    return Style(
        label_font_size=_round_half_up(LABEL_FONT_INCHES * dpi),
        title_font_size=_round_half_up(TITLE_FONT_INCHES * dpi),
        outline_thickness=_round_half_up(OUTLINE_THICKNESS_INCHES * dpi),
        line_width=_round_half_up(LINE_WIDTH_INCHES * dpi),
        corner_radius=_round_half_up(CORNER_RADIUS_INCHES * dpi),
    )


def _round_half_up(pixels: float) -> int:
    # Python's round() sends halves to the nearest even number, so 752.5 would become 752.
    return math.floor(round(pixels, PIXEL_PRECISION) + 0.5)
