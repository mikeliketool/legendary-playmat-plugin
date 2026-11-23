"""Tests for layout.transforms beyond the acceptance tests: error messages and how the parts fit together."""

import pytest
from layout.structs import Layout, UnknownCellError
from layout.transforms import find_cell, layout_for
from printing_spec.consts import SAFE_MARGIN, Mat
from printing_spec.structs import MatBox

LAYOUT_CHOICES = [(Mat.STANDARD, False), (Mat.OVERSIZE, False), (Mat.OVERSIZE, True)]


def all_boxes(layout: Layout) -> list[MatBox]:
    city = layout.city
    boxes = [box for cell in layout.cells for box in (cell.label_box, cell.card)]
    boxes += [city.outline, city.title_box, city.label_strip, *(district.label_box for district in city.districts)]
    return [*boxes, layout.hq.outline, layout.hq.title_box]


def test_extra_cell_error_says_which_mat_has_one() -> None:
    with pytest.raises(ValueError, match="Only the 28x14 mat has an extra cell"):
        layout_for(Mat.STANDARD, include_extra_cell=True)


def test_unknown_cell_error_is_a_key_error_with_a_plain_message() -> None:
    # str() of a plain KeyError wraps its message in quotes, which a user shouldn't see.
    with pytest.raises(UnknownCellError) as error:
        find_cell(layout_for(Mat.STANDARD), "extra")
    assert isinstance(error.value, KeyError)
    assert str(error.value) == "No cell with key 'extra' in this 24x14 layout."


# How the parts of a layout fit together.


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_each_card_sits_directly_under_its_label(mat: Mat, extra: bool) -> None:
    for cell in layout_for(mat, include_extra_cell=extra).cells:
        assert cell.card.left == cell.label_box.left, cell.key
        assert cell.card.width == cell.label_box.width, cell.key
        assert cell.card.top == pytest.approx(cell.label_box.bottom), cell.key


@pytest.mark.parametrize(("mat", "extra"), LAYOUT_CHOICES)
def test_everything_stays_inside_the_safe_margin(mat: Mat, extra: bool) -> None:
    for box in all_boxes(layout_for(mat, include_extra_cell=extra)):
        assert box.left >= SAFE_MARGIN and box.top >= SAFE_MARGIN, box
        assert box.right <= mat.width - SAFE_MARGIN and box.bottom <= mat.height - SAFE_MARGIN, box


@pytest.mark.parametrize("mat", [Mat.STANDARD, Mat.OVERSIZE])
def test_district_label_boxes_split_the_label_strip_into_fifths(mat: Mat) -> None:
    city = layout_for(mat).city
    strip = city.label_strip
    boxes = [district.label_box for district in city.districts]
    assert boxes[0].left == strip.left
    assert boxes[-1].right == pytest.approx(strip.right)
    for box in boxes:
        assert (box.top, box.height) == (strip.top, strip.height)
        assert box.width == pytest.approx(strip.width / 5)
    for divider_x, box in zip(city.divider_xs, boxes[1:], strict=True):
        assert divider_x == pytest.approx(box.left)


@pytest.mark.parametrize("mat", [Mat.STANDARD, Mat.OVERSIZE])
def test_city_sits_above_the_hq_with_the_same_width(mat: Mat) -> None:
    layout = layout_for(mat)
    assert layout.city.outline.left == layout.hq.outline.left
    assert layout.city.outline.width == layout.hq.outline.width
    assert layout.city.outline.bottom < layout.hq.outline.top
