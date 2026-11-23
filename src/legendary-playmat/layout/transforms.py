"""Layout rules for a Marvel Legendary playmat: where each cell goes on the mat, and finding a cell by its key.

Pure Python with no GIMP code, so the layout can be tested on its own. Everything is in inches from the trim.
"""

from printing_spec.consts import Mat
from printing_spec.structs import MatBox

from layout.consts import (
    CARD_HEIGHT,
    CARD_WIDTH,
    CELL_GRIDS,
    COLUMN_GAP,
    EXTRA_CELL,
    LABEL_HEIGHT,
    LABELS,
    MARGIN_LEFT_TOP,
    MARGIN_RIGHT_BOTTOM,
    ROW_TOPS,
)
from layout.structs import Cell, Layout, UnknownCellError


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
        _cell(key, columns[column], ROW_TOPS[row])
        for row, keys in enumerate(CELL_GRIDS[mat])
        for column, key in enumerate(keys)
        if key is not None and (key != EXTRA_CELL or include_extra_cell)
    )
    return Layout(mat, cells)


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
    """Left edge of each column of cells: the last two are measured from the right trim, the others from the left."""
    step = CARD_WIDTH + COLUMN_GAP
    first = MARGIN_LEFT_TOP
    last = mat.width - MARGIN_RIGHT_BOTTOM - CARD_WIDTH
    match mat:
        case Mat.STANDARD:
            return (first, first + step, first + 2 * step, last - step, last)
        case Mat.OVERSIZE:
            return (first, first + step, last - step, last)


def _cell(key: str, left: float, top: float) -> Cell:
    label_box = MatBox(left, top, CARD_WIDTH, LABEL_HEIGHT)
    card = MatBox(left, label_box.bottom, CARD_WIDTH, CARD_HEIGHT)
    return Cell(key, LABELS[key], label_box, card)
