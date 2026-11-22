"""Print spec for a Marvel Legendary playmat: mat sizes, print settings, and the inches-to-pixels rule.

Pure Python with no GIMP code, so it can be tested on its own. Positions are in inches from the top-left corner of
the trim (the finished mat's edge), and only become pixels at drawing time.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final

MIN_DPI: Final = 150
MAX_DPI: Final = 600
MAX_BLEED: Final = 0.5  # inches. The smallest bleed is 0.

# Inches typed as decimals aren't exact in binary floating point, so 0.29 x 200 comes out as 57.99999999999999.
# Rounding a product to this many decimal places first lets a whole or half pixel on paper round as one.
_PIXEL_PRECISION: Final = 9

# The measurements below come from the old GIMP 2 plugin, which worked in pixels at 150 DPI, so each one is written
# as old pixels / 150. The old canvas had a 1/4" bleed, which put the trim 37 px in from its left and top edges and
# 38 px in from its right and bottom edges. The old 115 px gap from the canvas edge is therefore 78 px from the
# left and top of the trim, and 77 px from the right and bottom.
_MARGIN_LEFT_TOP: Final = 78 / 150
_MARGIN_RIGHT_BOTTOM: Final = 77 / 150
_CARD_WIDTH: Final = 2.5  # 375 px
_CARD_HEIGHT: Final = 3.5  # 525 px
_LABEL_HEIGHT: Final = 65 / 150
_ROW_GAP: Final = 85 / 150
_COLUMN_GAP: Final = 70 / 150
_ROW_TOPS: Final = tuple(_MARGIN_LEFT_TOP + row * (_LABEL_HEIGHT + _CARD_HEIGHT + _ROW_GAP) for row in range(3))

# Sizes in inches that become pixels at the print DPI.
_LABEL_FONT_SIZE: Final = 54 / 150
_TITLE_FONT_SIZE: Final = 150 / 150
_OUTLINE_THICKNESS: Final = 3 / 150
_LINE_WIDTH: Final = 3 / 150
_CORNER_RADIUS: Final = 30 / 150

_EXTRA_CELL: Final = "extra"
_LABELS: Final[Mapping[str, str]] = {
    _EXTRA_CELL: "",
    "mastermind": "Mastermind",
    "scheme": "Scheme",
    "escaped": "Escaped",
    "strikes": "Strikes",
    "twists": "Twists",
    "bystanders": "Bystanders",
    "shield": "S.H.I.E.L.D.",
    "sidekicks": "Sidekicks",
    "wounds": "Wounds",
    "villain-deck": "Villain Deck",
    "hero-deck": "Hero Deck",
}


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


# Each mat's cells by row and column, as they appear on the mat. The City and HQ fill the empty middle.
_CELL_GRIDS: Final[Mapping[Mat, tuple[tuple[str | None, ...], ...]]] = {
    Mat.STANDARD: (
        ("scheme", "twists", "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", None, None, "villain-deck"),
        ("shield", "sidekicks", None, None, "hero-deck"),
    ),
    Mat.OVERSIZE: (
        (_EXTRA_CELL, "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", "villain-deck", "shield"),
        ("scheme", "twists", "hero-deck", "sidekicks"),
    ),
}


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
class Cell:
    """A card cell: a label box with the card area below it.

    The key never changes and is what a cell's layer group records. The label is the text drawn on the mat.
    """

    key: str
    label: str
    label_box: Rect
    card: Rect


class UnknownCellError(KeyError):
    """A layout has no cell with the requested key.

    It's a KeyError, so code that expects one still works. Unlike a plain KeyError, its message reads as plain text
    instead of being wrapped in quotes, so it can be shown to the user as it is.
    """

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


@dataclass(frozen=True)
class Layout:
    """Everything drawn on one mat, in inches from the trim."""

    mat: Mat
    cells: tuple[Cell, ...]

    def cell(self, key: str) -> Cell:
        """Find a cell by its key.

        Args:
            key: The key saved on the cell's layer group, such as "mastermind".

        Returns:
            The cell with that key.

        Raises:
            UnknownCellError: If this layout has no cell with that key. It's a KeyError, and its message names the
                key.
        """
        for cell in self.cells:
            if cell.key == key:
                return cell
        raise UnknownCellError(f"No cell with key {key!r} in this {_size_name(self.mat)} layout.")


@dataclass(frozen=True)
class Style:
    """Sizes in pixels that scale with DPI."""

    label_font_size: int
    title_font_size: int
    outline_thickness: int
    line_width: int
    corner_radius: int


def layout_for(mat: Mat, include_extra_cell: bool = False) -> Layout:
    """Build the layout for a mat.

    Args:
        mat: Which mat size to lay out.
        include_extra_cell: Whether to add the blank cell in the 28x14 mat's top-left corner.

    Returns:
        Every cell, in inches from the trim.

    Raises:
        ValueError: If include_extra_cell is True for a mat that has no extra cell (the 24x14).
    """
    if include_extra_cell and mat is not Mat.OVERSIZE:
        raise ValueError(f"Only the 28x14 mat has an extra cell, so the {_size_name(mat)} mat can't include one.")
    columns = _column_lefts(mat)
    cells = tuple(
        _cell(key, columns[column], _ROW_TOPS[row])
        for row, keys in enumerate(_CELL_GRIDS[mat])
        for column, key in enumerate(keys)
        if key is not None and (key != _EXTRA_CELL or include_extra_cell)
    )
    return Layout(mat, cells)


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
        label_font_size=_round_half_up(_LABEL_FONT_SIZE * dpi),
        title_font_size=_round_half_up(_TITLE_FONT_SIZE * dpi),
        outline_thickness=_round_half_up(_OUTLINE_THICKNESS * dpi),
        line_width=_round_half_up(_LINE_WIDTH * dpi),
        corner_radius=_round_half_up(_CORNER_RADIUS * dpi),
    )


def _round_half_up(pixels: float) -> int:
    # Python's round() sends halves to the nearest even number, so 752.5 would become 752.
    return math.floor(round(pixels, _PIXEL_PRECISION) + 0.5)


def _size_name(mat: Mat) -> str:
    return f"{mat.width:g}x{mat.height:g}"


def _column_lefts(mat: Mat) -> tuple[float, ...]:
    """Left edge of each column of cells: the last two are measured from the right trim, the others from the left."""
    step = _CARD_WIDTH + _COLUMN_GAP
    first = _MARGIN_LEFT_TOP
    last = mat.width - _MARGIN_RIGHT_BOTTOM - _CARD_WIDTH
    match mat:
        case Mat.STANDARD:
            return (first, first + step, first + 2 * step, last - step, last)
        case Mat.OVERSIZE:
            return (first, first + step, last - step, last)


def _cell(key: str, left: float, top: float) -> Cell:
    label_box = Rect(left, top, _CARD_WIDTH, _LABEL_HEIGHT)
    card = Rect(left, label_box.bottom, _CARD_WIDTH, _CARD_HEIGHT)
    return Cell(key, _LABELS[key], label_box, card)
