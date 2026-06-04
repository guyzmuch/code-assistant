import pytest

from utils.text import (
    apply_for_all_lines,
    first_non_empty_line,
    flatten_and_remove_empty_lines,
    require_input,
    merge_lines_into_one,
)


class TestRequireInput:
    def test_passes_when_lines_exist(self):
        require_input(["a"])

    def test_raises_when_input_is_empty(self):
        with pytest.raises(ValueError, match="no input provided"):
            require_input([])


class TestFirstNonEmptyLine:
    def test_returns_first_non_empty_line(self):
        assert first_non_empty_line(["", "  a  ", "b"]) == "  a  "

    def test_raises_when_input_is_empty(self):
        with pytest.raises(ValueError, match="no input provided"):
            first_non_empty_line([])

    def test_raises_when_all_lines_are_empty(self):
        with pytest.raises(ValueError, match="no non-empty line found"):
            first_non_empty_line(["", "   "])


class TestMergeLinesIntoOne:
    def test_joins_and_strips_lines(self):
        assert merge_lines_into_one(["  {", '"a": 1', "}  "]) == '{\n"a": 1\n}'

    def test_raises_when_input_is_empty(self):
        with pytest.raises(ValueError, match="no input provided"):
            merge_lines_into_one([])

    def test_raises_when_all_lines_are_whitespace(self):
        with pytest.raises(ValueError, match="no non-empty input found"):
            merge_lines_into_one(["", "   "])


class TestApplyForAllLines:
    def test_transforms_each_line(self):
        result = apply_for_all_lines(["1", "2"], lambda x: int(x) * 2)
        assert result == [2, 4]

    def test_preserves_empty_lines(self):
        result = apply_for_all_lines(["a", "", "b"], lambda x: x.upper())
        assert result == ["A", "", "B"]

    def test_catches_errors(self):
        result = apply_for_all_lines(["1", "bad"], int)
        assert result[0] == 1
        assert result[1] == "Error: invalid literal for int() with base 10: 'bad'"


class TestFlattenAndRemoveEmptyLines:
    def test_flattens_nested_lists(self):
        result = flatten_and_remove_empty_lines([["a", "b"], ["c"]])
        assert result == ["a", "b", "c"]

    def test_skips_empty_items(self):
        result = flatten_and_remove_empty_lines([["a", "", "b"], ["", "c"]])
        assert result == ["a", "b", "c"]
