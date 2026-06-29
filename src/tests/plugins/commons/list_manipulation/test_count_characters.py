from plugins.commons.list_manipulation.count_characters import CountCharacters


class TestCountCharacters:
    def test_counts_all_characters(self):
        plugin = CountCharacters()
        result = plugin.run(["hi!", "a b"])

        assert result == ["6"]

    def test_exclude_spaces(self):
        plugin = CountCharacters(options='{"exclude_spaces": true}')
        result = plugin.run(["hi there", "a b"])

        assert result == ["9"]

    def test_exclude_symbols(self):
        plugin = CountCharacters(options='{"exclude_symbols": true}')
        result = plugin.run(["hi!", "a-b"])

        assert result == ["4"]

    def test_exclude_spaces_and_symbols(self):
        plugin = CountCharacters(
            options='{"exclude_spaces": true, "exclude_symbols": true}'
        )
        result = plugin.run(["hi!", "a b"])

        assert result == ["4"]

    def test_empty_input_returns_zero(self):
        plugin = CountCharacters()
        result = plugin.run([])

        assert result == ["0"]
