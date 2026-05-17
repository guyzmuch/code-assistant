from plugins.commons.string_manipulation.split_by_separator import SplitBySeparator


class TestSplitBySeparator:
    def test_splits_single_line_by_comma(self):
        plugin = SplitBySeparator()
        result = plugin.run(["apple , banana , cherry"])

        assert result == ["apple", "banana", "cherry"]

    def test_splits_multiple_lines_and_flattens(self):
        plugin = SplitBySeparator()
        result = plugin.run([
            "a, b",
            "c,d"
        ])

        assert result == ["a", "b", "c", "d"]

    def test_uses_custom_separator_without_trim(self):
        plugin = SplitBySeparator(options='{"separator": ";", "trim": false}')
        result = plugin.run(["a; b;c"])

        assert result == ["a", " b", "c"]
