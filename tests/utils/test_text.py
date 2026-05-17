from utils.text import apply_for_all_lines, flatten_and_remove_empty_lines


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
