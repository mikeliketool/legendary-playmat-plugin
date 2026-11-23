"""Acceptance tests for the layout: where each cell, the City, and the HQ go on each mat.

At 150 DPI with a 1/4" bleed, every box must land where it is on the existing mats, except the City's district label
boxes (see test_city_matches_the_existing_mats). The constants below are positions and sizes on the existing mats,
in pixels on Inked Gaming's 150 DPI template, bleed included.
"""

from itertools import combinations

import pytest
from layout.structs import Layout
from layout.transforms import find_cell, layout_for
from printing_spec.consts import Mat
from printing_spec.structs import (
    MatBox,
    PrintSettings,
)
from printing_spec.transforms import (
    position_to_pixels,
    to_canvas,
    trim_offset,
)

CELL_WIDTH = 375
CELL_HEIGHT = 525
LABEL_HEIGHT = 65
CITY_AND_HQ_WIDTH = 2070
CITY_AND_HQ_HEIGHT = 600
TITLE_HEIGHT = 200
ROW_GAP = 85
COLUMN_GAP = 70
EDGE_GAP = 115
OVERSIZE_GAP_BEFORE_CITY_AND_HQ = 162.5
FIRST_ROW_Y = EDGE_GAP
SECOND_ROW_Y = EDGE_GAP + LABEL_HEIGHT + CELL_HEIGHT + ROW_GAP
THIRD_ROW_Y = SECOND_ROW_Y + LABEL_HEIGHT + CELL_HEIGHT + ROW_GAP
FIRST_COLUMN_X = EDGE_GAP
SECOND_COLUMN_X = EDGE_GAP + CELL_WIDTH + COLUMN_GAP
DISTRICT_WIDTH = CITY_AND_HQ_WIDTH / 5
DISTRICTS = ("Bridge", "Streets", "Rooftops", "Bank", "Sewers")

TEMPLATE_SIZES = {Mat.STANDARD: (3675, 2175), Mat.OVERSIZE: (4275, 2175)}

LABELS = {
    "extra": "",
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

MATS = [Mat.STANDARD, Mat.OVERSIZE]
LAYOUT_CHOICES = [(Mat.STANDARD, False), (Mat.OVERSIZE, False), (Mat.OVERSIZE, True)]
DPIS = [150, 300, 301, 600]
BLEEDS = [0.0, 0.125, 0.25, 0.5]


def existing_cell_positions(mat: Mat) -> dict[str, tuple[float, float]]:
    """Top-left corner of each cell's label box, by cell key, where it is on the existing mats."""
    width, _ = TEMPLATE_SIZES[mat]
    last_column_x = width - EDGE_GAP - CELL_WIDTH
    second_last_column_x = last_column_x - CELL_WIDTH - COLUMN_GAP
    if mat is Mat.OVERSIZE:
        return {
            "extra": (FIRST_COLUMN_X, FIRST_ROW_Y),
            "mastermind": (FIRST_COLUMN_X, SECOND_ROW_Y),
            "scheme": (FIRST_COLUMN_X, THIRD_ROW_Y),
            "escaped": (SECOND_COLUMN_X, FIRST_ROW_Y),
            "strikes": (SECOND_COLUMN_X, SECOND_ROW_Y),
            "twists": (SECOND_COLUMN_X, THIRD_ROW_Y),
            "bystanders": (last_column_x, FIRST_ROW_Y),
            "shield": (last_column_x, SECOND_ROW_Y),
            "sidekicks": (last_column_x, THIRD_ROW_Y),
            "wounds": (second_last_column_x, FIRST_ROW_Y),
            "villain-deck": (second_last_column_x, SECOND_ROW_Y),
            "hero-deck": (second_last_column_x, THIRD_ROW_Y),
        }
    third_column_x = SECOND_COLUMN_X + CELL_WIDTH + COLUMN_GAP
    return {
        "scheme": (FIRST_COLUMN_X, FIRST_ROW_Y),
        "mastermind": (FIRST_COLUMN_X, SECOND_ROW_Y),
        "shield": (FIRST_COLUMN_X, THIRD_ROW_Y),
        "twists": (SECOND_COLUMN_X, FIRST_ROW_Y),
        "strikes": (SECOND_COLUMN_X, SECOND_ROW_Y),
        "sidekicks": (SECOND_COLUMN_X, THIRD_ROW_Y),
        "bystanders": (last_column_x, FIRST_ROW_Y),
        "villain-deck": (last_column_x, SECOND_ROW_Y),
        "hero-deck": (last_column_x, THIRD_ROW_Y),
        "wounds": (second_last_column_x, FIRST_ROW_Y),
        "escaped": (third_column_x, FIRST_ROW_Y),
    }


def existing_city_and_hq_x(mat: Mat) -> float:
    """Left edge of the City and HQ on the existing mats."""
    if mat is Mat.OVERSIZE:
        return EDGE_GAP + CELL_WIDTH * 2 + COLUMN_GAP + OVERSIZE_GAP_BEFORE_CITY_AND_HQ
    return EDGE_GAP + CELL_WIDTH * 2 + COLUMN_GAP * 2 + 15


def existing_hq_y(mat: Mat) -> int:
    """Top edge of the HQ on the existing mats."""
    return TEMPLATE_SIZES[mat][1] - EDGE_GAP - CITY_AND_HQ_HEIGHT


def assert_matches_existing(box: MatBox, x: float, y: float, width: float, height: float) -> None:
    """At the default settings the box lands on the existing mat's box, within half a pixel at half-pixel edges."""
    px = to_canvas(box, PrintSettings())
    edges = [(px.x, x), (px.y, y), (px.x + px.width, x + width), (px.y + px.height, y + height)]
    for actual, expected in edges:
        assert abs(actual - expected) <= 0.5, f"{px} doesn't match the existing box {(x, y, width, height)}"


def element_parts(layout: Layout) -> list[list[MatBox]]:
    """Every drawn element (each cell, the City, the HQ) as the list of boxes it's made of."""
    city = layout.city
    elements = [[cell.label_box, cell.card] for cell in layout.cells]
    elements.append([city.outline, city.title_box, city.label_strip, *(d.label_box for d in city.districts)])
    elements.append([layout.hq.outline, layout.hq.title_box])
    return elements


def bounds(boxes: list[MatBox]) -> MatBox:
    left = min(b.left for b in boxes)
    top = min(b.top for b in boxes)
    return MatBox(left, top, max(b.right for b in boxes) - left, max(b.bottom for b in boxes) - top)


def overlaps(a: MatBox, b: MatBox) -> bool:
    return a.left < b.right and b.left < a.right and a.top < b.bottom and b.top < a.bottom


def test_standard_mat_has_eleven_cells() -> None:
    keys = {cell.key for cell in layout_for(Mat.STANDARD).cells}
    assert keys == set(existing_cell_positions(Mat.STANDARD))


def test_oversize_mat_adds_the_extra_cell_only_when_asked() -> None:
    without = {cell.key for cell in layout_for(Mat.OVERSIZE).cells}
    with_extra = {cell.key for cell in layout_for(Mat.OVERSIZE, include_extra_cell=True).cells}
    assert with_extra == set(existing_cell_positions(Mat.OVERSIZE))
    assert without == with_extra - {"extra"}


def test_standard_mat_has_no_extra_cell() -> None:
    with pytest.raises(ValueError):
        layout_for(Mat.STANDARD, include_extra_cell=True)


@pytest.mark.parametrize("mat", MATS)
def test_cells_match_the_existing_mats(mat: Mat) -> None:
    layout = layout_for(mat, include_extra_cell=mat is Mat.OVERSIZE)
    for key, (x, y) in existing_cell_positions(mat).items():
        cell = find_cell(layout, key)
        assert_matches_existing(cell.label_box, x, y, CELL_WIDTH, LABEL_HEIGHT)
        assert_matches_existing(cell.card, x, y + LABEL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)


@pytest.mark.parametrize("mat", MATS)
def test_hq_matches_the_existing_mats(mat: Mat) -> None:
    hq = layout_for(mat).hq
    x, y = existing_city_and_hq_x(mat), existing_hq_y(mat)
    assert_matches_existing(hq.outline, x, y, CITY_AND_HQ_WIDTH, CITY_AND_HQ_HEIGHT)
    assert_matches_existing(hq.title_box, x, y, CITY_AND_HQ_WIDTH, TITLE_HEIGHT)


@pytest.mark.parametrize("mat", MATS)
def test_city_matches_the_existing_mats(mat: Mat) -> None:
    city = layout_for(mat).city
    x, y = existing_city_and_hq_x(mat), existing_hq_y(mat) - ROW_GAP - CITY_AND_HQ_HEIGHT
    strip_y = y + CITY_AND_HQ_HEIGHT * 0.75
    strip_height = CITY_AND_HQ_HEIGHT / 4
    assert_matches_existing(city.outline, x, y, CITY_AND_HQ_WIDTH, CITY_AND_HQ_HEIGHT)
    assert_matches_existing(city.title_box, x, y, CITY_AND_HQ_WIDTH, TITLE_HEIGHT)
    assert_matches_existing(city.label_strip, x, strip_y, CITY_AND_HQ_WIDTH, strip_height)
    assert len(city.divider_xs) == 4
    for number, divider_x in enumerate(city.divider_xs, start=1):
        assert abs(position_to_pixels(divider_x, PrintSettings()) - (x + DISTRICT_WIDTH * number)) <= 0.5
    assert tuple(district.name for district in city.districts) == DISTRICTS
    # On the existing mats the district names start a third of the way down the strip and hang below the City.
    # Here each district's label box is its fifth of the label strip, so text drawn in it stays inside the City.
    for number, district in enumerate(city.districts):
        district_x = x + DISTRICT_WIDTH * number
        assert_matches_existing(district.label_box, district_x, strip_y, DISTRICT_WIDTH, strip_height)


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_no_two_elements_overlap(mat: Mat, extra: bool) -> None:
    element_bounds = [bounds(parts) for parts in element_parts(layout_for(mat, include_extra_cell=extra))]
    for a, b in combinations(element_bounds, 2):
        assert not overlaps(a, b), f"{a} overlaps {b}"


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_everything_is_inside_the_safe_area(mat: Mat, extra: bool) -> None:
    for parts in element_parts(layout_for(mat, include_extra_cell=extra)):
        for box in parts:
            assert box.left >= 0.5 and box.top >= 0.5, box
            assert box.right <= mat.width - 0.5 and box.bottom <= mat.height - 0.5, box


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_cards_are_two_and_a_half_by_three_and_a_half_inches(mat: Mat, extra: bool) -> None:
    for cell in layout_for(mat, include_extra_cell=extra).cells:
        assert cell.card.width == pytest.approx(2.5) and cell.card.height == pytest.approx(3.5), cell.key


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
@pytest.mark.parametrize("dpi", DPIS)
@pytest.mark.parametrize("bleed", BLEEDS)
def test_cards_are_within_one_pixel_of_card_size(mat: Mat, extra: bool, dpi: int, bleed: float) -> None:
    settings = PrintSettings(dpi=dpi, bleed=bleed)
    for cell in layout_for(mat, include_extra_cell=extra).cells:
        card = to_canvas(cell.card, settings)
        assert abs(card.width - 2.5 * dpi) <= 1 and abs(card.height - 3.5 * dpi) <= 1, (cell.key, card)


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
@pytest.mark.parametrize("dpi", DPIS)
def test_positions_from_the_trim_do_not_depend_on_the_bleed(mat: Mat, extra: bool, dpi: int) -> None:
    boxes = [box for parts in element_parts(layout_for(mat, include_extra_cell=extra)) for box in parts]

    def from_trim(bleed: float) -> list[tuple[int, int, int, int]]:
        settings = PrintSettings(dpi=dpi, bleed=bleed)
        offset = trim_offset(settings)
        canvas_boxes = [to_canvas(box, settings) for box in boxes]
        return [(px.x - offset, px.y - offset, px.width, px.height) for px in canvas_boxes]

    first, *others = [from_trim(bleed) for bleed in BLEEDS]
    for other in others:
        assert other == first


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_cells_have_unique_keys_and_correctly_spelled_labels(mat: Mat, extra: bool) -> None:
    cells = layout_for(mat, include_extra_cell=extra).cells
    assert len({cell.key for cell in cells}) == len(cells)
    for cell in cells:
        assert cell.label == LABELS[cell.key]


def test_a_cell_is_found_by_its_key() -> None:
    layout = layout_for(Mat.OVERSIZE, include_extra_cell=True)
    assert find_cell(layout, "mastermind").label == "Mastermind"
    assert find_cell(layout, "shield").label == "S.H.I.E.L.D."
    assert find_cell(layout, "villain-deck").label == "Villain Deck"
    assert find_cell(layout, "extra").label == ""


def test_an_unknown_cell_key_fails_clearly() -> None:
    with pytest.raises(KeyError, match="no-such-cell"):
        find_cell(layout_for(Mat.STANDARD), "no-such-cell")


def test_the_extra_cell_is_not_found_when_it_is_left_out() -> None:
    with pytest.raises(KeyError, match="extra"):
        find_cell(layout_for(Mat.OVERSIZE), "extra")
