"""Layout rules for a Marvel Legendary playmat: where each cell, the City and the HQ go, and finding a cell by key.

Pure Python with no GIMP code, so the layout can be tested on its own. Everything is in inches from the trim.
"""

from printing_spec.consts import Mat
from printing_spec.structs import MatBox

from layout.consts import (
    CARD_HEIGHT,
    CARD_WIDTH,
    CITY_AND_HQ_HEIGHT,
    CITY_AND_HQ_SPACE,
    CITY_AND_HQ_WIDTH,
    COLUMN_GAP,
    DISTRICT_NAMES,
    EXTRA_CELL,
    LABEL_HEIGHT,
    LABEL_STRIP_HEIGHT,
    LABELS,
    MARGIN_LEFT_TOP,
    MARGIN_RIGHT_BOTTOM,
    MAT_LAYOUTS,
    ROW_GAP,
    ROW_TOPS,
    TITLE_HEIGHT,
)
from layout.structs import (
    Cell,
    City,
    District,
    Headquarters,
    Layout,
    UnknownCellError,
)


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
    if include_extra_cell and not has_extra_cell(mat):
        raise ValueError(f"Only the 28x14 mat has an extra cell, so the {_size_name(mat)} mat can't include one.")
    mat_layout = MAT_LAYOUTS[mat]
    columns = _column_lefts(mat)
    cells = tuple(
        _cell_at(key, columns[column], ROW_TOPS[row])
        for row, keys in enumerate(mat_layout.cell_grid)
        for column, key in enumerate(keys)
        if key is not CITY_AND_HQ_SPACE and (key != EXTRA_CELL or include_extra_cell)
    )
    city_and_hq_left = columns[1] + CARD_WIDTH + mat_layout.gap_before_city_and_hq
    hq_top = mat.height - MARGIN_RIGHT_BOTTOM - CITY_AND_HQ_HEIGHT
    city_top = hq_top - ROW_GAP - CITY_AND_HQ_HEIGHT
    return Layout(mat, cells, _city(city_and_hq_left, city_top), _headquarters(city_and_hq_left, hq_top))


def has_extra_cell(mat: Mat) -> bool:
    """Say whether a mat has the optional blank cell in its top-left corner.

    Args:
        mat: Which mat size to ask about.

    Returns:
        True if layout_for can include the extra cell for this mat (the 28x14), False if it can't (the 24x14).
    """
    return any(EXTRA_CELL in row for row in MAT_LAYOUTS[mat].cell_grid)


def find_cell(layout: Layout, key: str) -> Cell:
    """Find a cell by its key.

    Args:
        layout: The layout to search.
        key: The key saved on the cell's layer group, such as "mastermind".

    Returns:
        The cell with that key.

    Raises:
        UnknownCellError: If the layout has no cell with that key. It's a KeyError, and its message names the key.
    """
    for cell in layout.cells:
        if cell.key == key:
            return cell
    raise UnknownCellError(f"No cell with key {key!r} in this {_size_name(layout.mat)} layout.")


def _size_name(mat: Mat) -> str:
    return f"{mat.width:g}x{mat.height:g}"


def _column_lefts(mat: Mat) -> tuple[float, ...]:
    """Left edge of each column of cells: the first few from the left margin, the rest from the right trim."""
    mat_layout = MAT_LAYOUTS[mat]
    step = CARD_WIDTH + COLUMN_GAP
    last = mat.width - MARGIN_RIGHT_BOTTOM - CARD_WIDTH
    count_from_left = mat_layout.columns_from_left
    count_from_right = len(mat_layout.cell_grid[0]) - count_from_left
    from_left_margin = tuple(MARGIN_LEFT_TOP + n * step for n in range(count_from_left))
    from_right_trim = tuple(last - n * step for n in reversed(range(count_from_right)))
    return from_left_margin + from_right_trim


def _cell_at(key: str, left: float, top: float) -> Cell:
    label_box = MatBox(left, top, CARD_WIDTH, LABEL_HEIGHT)
    card = MatBox(left, label_box.bottom, CARD_WIDTH, CARD_HEIGHT)
    return Cell(key, LABELS[key], label_box, card)


def _city(left: float, top: float) -> City:
    strip = MatBox(left, top + CITY_AND_HQ_HEIGHT - LABEL_STRIP_HEIGHT, CITY_AND_HQ_WIDTH, LABEL_STRIP_HEIGHT)
    districts = _split_into_districts(strip)
    return City(
        outline=MatBox(left, top, CITY_AND_HQ_WIDTH, CITY_AND_HQ_HEIGHT),
        title_box=MatBox(left, top, CITY_AND_HQ_WIDTH, TITLE_HEIGHT),
        divider_xs=tuple(district.label_box.left for district in districts[1:]),
        label_strip=strip,
        districts=districts,
    )


def _split_into_districts(label_strip: MatBox) -> tuple[District, ...]:
    width = label_strip.width / len(DISTRICT_NAMES)
    return tuple(
        District(name, MatBox(label_strip.left + number * width, label_strip.top, width, label_strip.height))
        for number, name in enumerate(DISTRICT_NAMES)
    )


def _headquarters(left: float, top: float) -> Headquarters:
    return Headquarters(
        outline=MatBox(left, top, CITY_AND_HQ_WIDTH, CITY_AND_HQ_HEIGHT),
        title_box=MatBox(left, top, CITY_AND_HQ_WIDTH, TITLE_HEIGHT),
    )
