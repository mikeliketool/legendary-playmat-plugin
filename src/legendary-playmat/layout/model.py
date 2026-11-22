"""Layout of a Marvel Legendary playmat: where everything goes on the mat, in inches from the trim.

Pure Python with no GIMP code, so the layout can be tested on its own.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from print_spec.model import Mat, Rect

_GIMP2_DPI: Final = 150
# The GIMP 2 plugin's canvas had a 37.5 px bleed, which the trim rule splits as 37 px at the left and top and 38 px
# at the right and bottom. So its 115 px outside gap is 78 px from the left and top trim, and 77 px from the right
# and bottom.
_GIMP2_TRIM_LEFT_TOP: Final = 37
_GIMP2_TRIM_RIGHT_BOTTOM: Final = 38
_GIMP2_OUTSIDE_GAP: Final = 115
_MARGIN_LEFT_TOP: Final = (_GIMP2_OUTSIDE_GAP - _GIMP2_TRIM_LEFT_TOP) / _GIMP2_DPI
_MARGIN_RIGHT_BOTTOM: Final = (_GIMP2_OUTSIDE_GAP - _GIMP2_TRIM_RIGHT_BOTTOM) / _GIMP2_DPI
_CARD_WIDTH: Final = 2.5
_CARD_HEIGHT: Final = 3.5
_LABEL_HEIGHT: Final = 65 / _GIMP2_DPI
_ROW_GAP: Final = 85 / _GIMP2_DPI
_COLUMN_GAP: Final = 70 / _GIMP2_DPI
_CITY_AND_HQ_WIDTH: Final = 2070 / _GIMP2_DPI
_CITY_AND_HQ_HEIGHT: Final = 600 / _GIMP2_DPI
_TITLE_HEIGHT: Final = 200 / _GIMP2_DPI
_LABEL_STRIP_HEIGHT: Final = _CITY_AND_HQ_HEIGHT / 4
_ROW_TOPS: Final = tuple(_MARGIN_LEFT_TOP + row * (_LABEL_HEIGHT + _CARD_HEIGHT + _ROW_GAP) for row in range(3))

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

_GAP_BEFORE_CITY_AND_HQ: Final[Mapping[Mat, float]] = {
    Mat.STANDARD: (70 + 15) / _GIMP2_DPI,
    Mat.OVERSIZE: 162.5 / _GIMP2_DPI,
}


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
    """The City: an outline with a title, four vertical dividers, and a strip of district labels.

    Attributes:
        outline: The City's border.
        title_box: The box for the City's title, across the top of the outline.
        divider_xs: The x of each divider line, in inches from the trim's left edge. Each line runs the full height
            of the outline.
        label_strip: The strip across the bottom of the outline that holds the district labels.
        districts: The five districts, left to right. Each one's label box is its fifth of the label strip.
    """

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
        _cell_at(key, columns[column], _ROW_TOPS[row])
        for row, keys in enumerate(_CELL_GRIDS[mat])
        for column, key in enumerate(keys)
        if key is not _CITY_AND_HQ_SPACE and (key != _EXTRA_CELL or include_extra_cell)
    )
    city_and_hq_left = columns[1] + _CARD_WIDTH + _GAP_BEFORE_CITY_AND_HQ[mat]
    hq_top = mat.height - _MARGIN_RIGHT_BOTTOM - _CITY_AND_HQ_HEIGHT
    city_top = hq_top - _ROW_GAP - _CITY_AND_HQ_HEIGHT
    return Layout(mat, cells, _city(city_and_hq_left, city_top), _headquarters(city_and_hq_left, hq_top))


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


def _cell_at(key: str, left: float, top: float) -> Cell:
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
