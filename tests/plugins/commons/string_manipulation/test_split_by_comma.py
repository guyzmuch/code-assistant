from plugins.commons.string_manipulation.split_by_comma import SplitByComma


def test_splits_single_line_by_comma():
    plugin = SplitByComma()
    result = plugin.run(["apple , banana , cherry"])
    assert result == ["apple", "banana", "cherry"]


def test_splits_multiple_lines_and_flattens():
    plugin = SplitByComma()
    result = plugin.run(["a, b", "c,d"])
    assert result == ["a", "b", "c", "d"]
