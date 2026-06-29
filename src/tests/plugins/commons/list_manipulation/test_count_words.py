from plugins.commons.list_manipulation.count_words import CountWords


class TestCountWords:
    def test_counts_words_across_lines(self):
        plugin = CountWords()
        result = plugin.run(["hello world", "foo bar baz"])

        assert result == ["5"]

    def test_empty_line_counts_as_zero_words(self):
        plugin = CountWords()
        result = plugin.run(["hello", "", "world"])

        assert result == ["2"]

    def test_empty_input_returns_zero(self):
        plugin = CountWords()
        result = plugin.run([])

        assert result == ["0"]
