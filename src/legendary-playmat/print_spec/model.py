"""Print spec for a Marvel Legendary playmat: mat sizes, print settings, and the inches-to-pixels rule.

Pure Python with no GIMP code, so it can be tested on its own. Positions are in inches from the top-left corner of
the trim (the finished mat's edge), and only become pixels at drawing time.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

MIN_DPI: Final = 150
MAX_DPI: Final = 600
MAX_BLEED: Final = 0.5
# Inked Gaming's cut isn't exact, so text and important art stay this far inside the trim.
# https://www.inkedgaming.com/pages/art-instructions
SAFE_MARGIN: Final = 0.5

# Inches typed as decimals aren't exact in binary floating point, so 0.29 x 200 comes out as 57.99999999999999.
# Rounding a product to this many decimal places first lets a whole or half pixel on paper round as one.
_PIXEL_PRECISION: Final = 9

_GIMP2_DPI: Final = 150
_LABEL_FONT_INCHES: Final = 54 / _GIMP2_DPI
_TITLE_FONT_INCHES: Final = 150 / _GIMP2_DPI
_OUTLINE_THICKNESS_INCHES: Final = 3 / _GIMP2_DPI
_LINE_WIDTH_INCHES: Final = 3 / _GIMP2_DPI
_CORNER_RADIUS_INCHES: Final = 30 / _GIMP2_DPI


class Mat(Enum):
    """The two mat sizes Inked Gaming prints, as (width, height) of the trim in inches."""

    STANDARD = (24.0, 14.0)
    OVERSIZE = (28.0, 14.0)

    @property
    def width(self) -> float:
        """Trim width in inches."""
        return self.value[0]

    @property
    def height(self) -> float:
        """Trim height in inches."""
        return self.value[1]


@dataclass(frozen=True)
class PrintSettings:
    """Resolution and bleed for one print file.

    Attributes:
        dpi: Print resolution in dots per inch.
        bleed: Extra artwork past the trim on each side, in inches.

    Raises:
        ValueError: If dpi is outside 150-600 or bleed is outside 0-0.5 inches.
    """

    dpi: int = 150
    bleed: float = 0.25

    def __post_init__(self) -> None:
        if not MIN_DPI <= self.dpi <= MAX_DPI:
            raise ValueError(f"DPI must be between {MIN_DPI} and {MAX_DPI}, not {self.dpi}.")
        if not 0 <= self.bleed <= MAX_BLEED:
            raise ValueError(f"Bleed must be between 0 and {MAX_BLEED} inches, not {self.bleed}.")


@dataclass(frozen=True)
class PixelRect:
    """A box in pixels on the canvas, bleed included."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Rect:
    """A box in inches, measured from the top-left corner of the trim."""

    left: float
    top: float
    width: float
    height: float

    @property
    def right(self) -> float:
        """Right edge in inches from the trim's left edge."""
        return self.left + self.width

    @property
    def bottom(self) -> float:
        """Bottom edge in inches from the trim's top edge."""
        return self.top + self.height

    def to_pixels(self, settings: PrintSettings) -> PixelRect:
        """Convert to pixels: each edge goes through position_to_pixels, and the size comes from those edges.

        Args:
            settings: The DPI and bleed of the canvas.

        Returns:
            The box in canvas pixels, bleed included.
        """
        x = position_to_pixels(self.left, settings)
        y = position_to_pixels(self.top, settings)
        right = position_to_pixels(self.right, settings)
        bottom = position_to_pixels(self.bottom, settings)
        return PixelRect(x, y, right - x, bottom - y)


@dataclass(frozen=True)
class Style:
    """Sizes in pixels that scale with DPI."""

    label_font_size: int
    title_font_size: int
    outline_thickness: int
    line_width: int
    corner_radius: int


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
    return math.floor(round(settings.bleed * settings.dpi, _PIXEL_PRECISION))


def position_to_pixels(inches: float, settings: PrintSettings) -> int:
    """Canvas pixel for a position in inches from the trim: trim_offset + round(inches x DPI), halves rounded up.

    Args:
        inches: A distance from the trim's left edge (for x) or top edge (for y).
        settings: The DPI and bleed.

    Returns:
        The pixel's x or y on the canvas.
    """
    return trim_offset(settings) + _round_half_up(inches * settings.dpi)


def style_for(settings: PrintSettings) -> Style:
    """Font sizes, outline thickness, line width, and corner radius for these settings.

    Args:
        settings: The DPI and bleed. Only the DPI changes the sizes.

    Returns:
        The sizes in pixels. At 150 DPI they're the old plugin's sizes.
    """
    dpi = settings.dpi
    return Style(
        label_font_size=_round_half_up(_LABEL_FONT_INCHES * dpi),
        title_font_size=_round_half_up(_TITLE_FONT_INCHES * dpi),
        outline_thickness=_round_half_up(_OUTLINE_THICKNESS_INCHES * dpi),
        line_width=_round_half_up(_LINE_WIDTH_INCHES * dpi),
        corner_radius=_round_half_up(_CORNER_RADIUS_INCHES * dpi),
    )


def _round_half_up(pixels: float) -> int:
    # Python's round() sends halves to the nearest even number, so 752.5 would become 752.
    return math.floor(round(pixels, _PIXEL_PRECISION) + 0.5)
