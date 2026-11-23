"""Tests for layout.transforms beyond the acceptance tests: error messages and how the parts fit together."""

import pytest
from layout.structs import UnknownCellError
from layout.transforms import find_cell, layout_for
from printing_spec.consts import Mat

LAYOUT_CHOICES = [(Mat.STANDARD, False), (Mat.OVERSIZE, False), (Mat.OVERSIZE, True)]


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
