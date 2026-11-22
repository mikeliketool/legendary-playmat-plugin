"""Acceptance tests for layout.py, confirmed with the user before implementation.

At 150 DPI with a 1/4" bleed, the layout must reproduce the old GIMP 2 plugin exactly, except for the City's district
label boxes (see test_city_matches_the_old_plugin). The constants below are that plugin's pixel values, copied from
src/legendary_plugin_extension.py (tag gimp2-final). They're on a 150 DPI canvas that includes a 1/4" bleed.
"""

import pytest
from layout.model import layout_for
from print_spec.model import (
    Mat,
    PrintSettings,
    Rect,
)

CELL_WIDTH = 375
CELL_HEIGHT = 525
LABEL_HEIGHT = 65
ROW_GAP = 85
COLUMN_GAP = 70
OUTSIDE_GAP = 115
FIRST_ROW_Y = OUTSIDE_GAP
SECOND_ROW_Y = OUTSIDE_GAP + LABEL_HEIGHT + CELL_HEIGHT + ROW_GAP
THIRD_ROW_Y = SECOND_ROW_Y + LABEL_HEIGHT + CELL_HEIGHT + ROW_GAP
FIRST_COLUMN_X = OUTSIDE_GAP
SECOND_COLUMN_X = OUTSIDE_GAP + CELL_WIDTH + COLUMN_GAP

OLD_CANVAS = {Mat.STANDARD: (3675, 2175), Mat.OVERSIZE: (4275, 2175)}

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


def old_cell_positions(mat: Mat) -> dict[str, tuple[float, float]]:
    """Top-left corner of each cell's label box, by cell key, where the old plugin put it."""
    width, _ = OLD_CANVAS[mat]
    last_column_x = width - OUTSIDE_GAP - CELL_WIDTH
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


def assert_matches_old(rect: Rect, x: float, y: float, width: float, height: float) -> None:
    """At the default settings the rect lands on the old pixel box. Old half-pixel edges may be off by half a pixel."""
    px = rect.to_pixels(PrintSettings())
    edges = [(px.x, x), (px.y, y), (px.x + px.width, x + width), (px.y + px.height, y + height)]
    for actual, expected in edges:
        assert abs(actual - expected) <= 0.5, f"{px} doesn't match the old box {(x, y, width, height)}"


# 1. Mat sizes


def test_standard_mat_has_the_old_plugins_eleven_cells() -> None:
    keys = {cell.key for cell in layout_for(Mat.STANDARD).cells}
    assert keys == set(old_cell_positions(Mat.STANDARD))


def test_oversize_mat_adds_the_extra_cell_only_when_asked() -> None:
    without = {cell.key for cell in layout_for(Mat.OVERSIZE).cells}
    with_extra = {cell.key for cell in layout_for(Mat.OVERSIZE, include_extra_cell=True).cells}
    assert with_extra == set(old_cell_positions(Mat.OVERSIZE))
    assert without == with_extra - {"extra"}


def test_standard_mat_has_no_extra_cell() -> None:
    with pytest.raises(ValueError):
        layout_for(Mat.STANDARD, include_extra_cell=True)


# 4. Matches the old mats (150 DPI, 1/4" bleed)


@pytest.mark.parametrize("mat", MATS)
def test_cells_match_the_old_plugin(mat: Mat) -> None:
    layout = layout_for(mat, include_extra_cell=mat is Mat.OVERSIZE)
    for key, (x, y) in old_cell_positions(mat).items():
        cell = layout.cell(key)
        assert_matches_old(cell.label_box, x, y, CELL_WIDTH, LABEL_HEIGHT)
        assert_matches_old(cell.card, x, y + LABEL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)


# 6. Any setting


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
        card = cell.card.to_pixels(settings)
        assert abs(card.width - 2.5 * dpi) <= 1 and abs(card.height - 3.5 * dpi) <= 1, (cell.key, card)


# 7. Fixed labels and 8. Cell lookup


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_cells_have_unique_keys_and_correctly_spelled_labels(mat: Mat, extra: bool) -> None:
    cells = layout_for(mat, include_extra_cell=extra).cells
    assert len({cell.key for cell in cells}) == len(cells)
    for cell in cells:
        assert cell.label == LABELS[cell.key]


def test_a_cell_is_found_by_its_key() -> None:
    layout = layout_for(Mat.OVERSIZE, include_extra_cell=True)
    assert layout.cell("mastermind").label == "Mastermind"
    assert layout.cell("shield").label == "S.H.I.E.L.D."
    assert layout.cell("villain-deck").label == "Villain Deck"
    assert layout.cell("extra").label == ""


def test_an_unknown_cell_key_fails_clearly() -> None:
    with pytest.raises(KeyError, match="no-such-cell"):
        layout_for(Mat.STANDARD).cell("no-such-cell")


def test_the_extra_cell_is_not_found_when_it_is_left_out() -> None:
    with pytest.raises(KeyError, match="extra"):
        layout_for(Mat.OVERSIZE).cell("extra")
