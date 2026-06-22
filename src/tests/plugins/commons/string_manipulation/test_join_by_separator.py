from plugins.commons.string_manipulation.join_by_separator import JoinBySeparator


class TestJoinBySeparator:
    def test_joins_multiple_lines(self):
        plugin = JoinBySeparator()
        result = plugin.run(["apple", "banana", "cherry"])

        assert result == ["apple,banana,cherry"]

    def test_strips_whitespace(self):
        plugin = JoinBySeparator()
        result = plugin.run(["  apple  ", " banana "])

        assert result == ["apple,banana"]

    def test_joins_multiple_lines_but_not_split_lines(self):
        plugin = JoinBySeparator()
        result = plugin.run(["  apple  banana  ", "cherry"])

        assert result == ["apple  banana,cherry"]

    def test_skips_empty_lines(self):
        plugin = JoinBySeparator()
        result = plugin.run(["apple", "", "  ", "banana"])

        assert result == ["apple,banana"]

    def test_single_line(self):
        plugin = JoinBySeparator()
        result = plugin.run(["only-one"])

        assert result == ["only-one"]

    def test_empty_input_returns_empty_string(self):
        plugin = JoinBySeparator()
        result = plugin.run([])

        assert result == [""]

    def test_uses_custom_separator_without_trim(self):
        plugin = JoinBySeparator(options='{"separator": ";", "trim": false}')
        result = plugin.run(["  apple  ", " banana "])

        assert result == ["  apple  ; banana "]

    def test_keeps_empty_lines_when_skip_disabled(self):
        plugin = JoinBySeparator(options='{"skip_empty_lines": false}')
        result = plugin.run(["apple", "", "  ", "banana"])

        assert result == ["apple,,,banana"]
