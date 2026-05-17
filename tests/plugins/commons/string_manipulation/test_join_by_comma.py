from plugins.commons.string_manipulation.join_by_comma import JoinByComma


class TestJoinByComma:
    def test_joins_multiple_lines(self):
        plugin = JoinByComma()
        result = plugin.run(["apple", "banana", "cherry"])

        assert result == ["apple,banana,cherry"]

    def test_strips_whitespace(self):
        plugin = JoinByComma()
        result = plugin.run(["  apple  ", " banana "])

        assert result == ["apple,banana"]

    def test_joins_multiple_lines_but_not_split_lines(self):
        plugin = JoinByComma()
        result = plugin.run(["  apple  banana  ", "cherry"])

        assert result == ["apple  banana,cherry"]

    def test_skips_empty_lines(self):
        plugin = JoinByComma()
        result = plugin.run(["apple", "", "  ", "banana"])

        assert result == ["apple,banana"]


    def test_single_line(self):
        plugin = JoinByComma()
        result = plugin.run(["only-one"])

        assert result == ["only-one"]

    def test_empty_input_returns_empty_string(self):
        plugin = JoinByComma()
        result = plugin.run([])

        assert result == [""]
