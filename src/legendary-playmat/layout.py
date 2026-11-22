"""Layout of a Marvel Legendary playmat: mat sizes, element positions, and the inches-to-pixels rule.

Pure Python with no GIMP code, so the layout can be tested on its own. Positions are in inches from the
top-left corner of the trim (the finished mat's edge), and only become pixels at drawing time.
"""

import math
from collections.abc import Mapping
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

_OLD_DPI: Final = 150
# The old GIMP 2 plugin's canvas had a 37.5 px bleed, which the trim rule splits as 37 px at the left and top and
# 38 px at the right and bottom. So its gaps from the canvas edge are a pixel smaller from the right and bottom trim.
_OLD_TRIM_LEFT_TOP: Final = 37
_OLD_TRIM_RIGHT_BOTTOM: Final = 38
_OLD_GAP_FROM_CANVAS_EDGE: Final = 115
_MARGIN_LEFT_TOP: Final = (_OLD_GAP_FROM_CANVAS_EDGE - _OLD_TRIM_LEFT_TOP) / _OLD_DPI
_MARGIN_RIGHT_BOTTOM: Final = (_OLD_GAP_FROM_CANVAS_EDGE - _OLD_TRIM_RIGHT_BOTTOM) / _OLD_DPI
_CARD_WIDTH: Final = 2.5
_CARD_HEIGHT: Final = 3.5
_LABEL_HEIGHT: Final = 65 / _OLD_DPI
_ROW_GAP: Final = 85 / _OLD_DPI
_COLUMN_GAP: Final = 70 / _OLD_DPI
_CITY_AND_HQ_WIDTH: Final = 2070 / _OLD_DPI
_CITY_AND_HQ_HEIGHT: Final = 600 / _OLD_DPI
_TITLE_HEIGHT: Final = 200 / _OLD_DPI
_LABEL_STRIP_HEIGHT: Final = _CITY_AND_HQ_HEIGHT / 4
_ROW_TOPS: Final = tuple(_MARGIN_LEFT_TOP + row * (_LABEL_HEIGHT + _CARD_HEIGHT + _ROW_GAP) for row in range(3))

_LABEL_FONT_SIZE: Final = 54 / _OLD_DPI
_TITLE_FONT_SIZE: Final = 150 / _OLD_DPI
_OUTLINE_THICKNESS: Final = 3 / _OLD_DPI
_LINE_WIDTH: Final = 3 / _OLD_DPI
_CORNER_RADIUS: Final = 30 / _OLD_DPI

_EXTRA_CELL: Final = "extra"
_CITY_AND_HQ_SPACE: Final = None
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
_DISTRICT_NAMES: Final = ("Bridge", "Streets", "Rooftops", "Bank", "Sewers")


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


_CELL_GRIDS: Final[Mapping[Mat, tuple[tuple[str | None, ...], ...]]] = {
    Mat.STANDARD: (
        ("scheme", "twists", "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", _CITY_AND_HQ_SPACE, _CITY_AND_HQ_SPACE, "villain-deck"),
        ("shield", "sidekicks", _CITY_AND_HQ_SPACE, _CITY_AND_HQ_SPACE, "hero-deck"),
    ),
    Mat.OVERSIZE: (
        (_EXTRA_CELL, "escaped", "wounds", "bystanders"),
        ("mastermind", "strikes", "villain-deck", "shield"),
        ("scheme", "twists", "hero-deck", "sidekicks"),
    ),
}

_GAP_AFTER_SECOND_COLUMN: Final[Mapping[Mat, float]] = {Mat.STANDARD: 85 / _OLD_DPI, Mat.OVERSIZE: 162.5 / _OLD_DPI}


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


@dataclass(frozen=True)
class District:
    """One of the City's five spaces, with its name label."""

    name: str
    label_box: Rect


@dataclass(frozen=True)
class City:
    """The City: an outline with a title, four vertical dividers, and a strip of district labels."""

    outline: Rect
    title_box: Rect
    divider_xs: tuple[float, ...]
    label_strip: Rect
    districts: tuple[District, ...]


@dataclass(frozen=True)
class Headquarters:
    """The HQ row: an outline with a title."""

    outline: Rect
    title_box: Rect


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
    city: City
    hq: Headquarters

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
        Every cell, the City, and the HQ, in inches from the trim.

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
        if key is not _CITY_AND_HQ_SPACE and (key != _EXTRA_CELL or include_extra_cell)
    )
    city_and_hq_left = columns[1] + _CARD_WIDTH + _GAP_AFTER_SECOND_COLUMN[mat]
    hq_top = mat.height - _MARGIN_RIGHT_BOTTOM - _CITY_AND_HQ_HEIGHT
    city_top = hq_top - _ROW_GAP - _CITY_AND_HQ_HEIGHT
    return Layout(mat, cells, _city(city_and_hq_left, city_top), _headquarters(city_and_hq_left, hq_top))


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


def _city(left: float, top: float) -> City:
    strip = Rect(left, top + _CITY_AND_HQ_HEIGHT - _LABEL_STRIP_HEIGHT, _CITY_AND_HQ_WIDTH, _LABEL_STRIP_HEIGHT)
    districts = _split_into_districts(strip)
    return City(
        outline=Rect(left, top, _CITY_AND_HQ_WIDTH, _CITY_AND_HQ_HEIGHT),
        title_box=Rect(left, top, _CITY_AND_HQ_WIDTH, _TITLE_HEIGHT),
        divider_xs=tuple(district.label_box.left for district in districts[1:]),
        label_strip=strip,
        districts=districts,
    )


def _split_into_districts(label_strip: Rect) -> tuple[District, ...]:
    width = label_strip.width / len(_DISTRICT_NAMES)
    return tuple(
        District(name, Rect(label_strip.left + number * width, label_strip.top, width, label_strip.height))
        for number, name in enumerate(_DISTRICT_NAMES)
    )


def _headquarters(left: float, top: float) -> Headquarters:
    return Headquarters(
        outline=Rect(left, top, _CITY_AND_HQ_WIDTH, _CITY_AND_HQ_HEIGHT),
        title_box=Rect(left, top, _CITY_AND_HQ_WIDTH, _TITLE_HEIGHT),
    )
