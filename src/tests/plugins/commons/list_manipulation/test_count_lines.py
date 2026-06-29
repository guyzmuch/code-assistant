from plugins.commons.list_manipulation.count_lines import CountLines


class TestCountLines:
    def test_counts_lines(self):
        plugin = CountLines()
        result = plugin.run(["apple", "banana", "", "cherry"])

        assert result == ["4"]

    def test_empty_input_returns_zero(self):
        plugin = CountLines()
        result = plugin.run([])

        assert result == ["0"]
