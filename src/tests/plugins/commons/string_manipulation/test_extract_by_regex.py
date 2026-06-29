from plugins.commons.string_manipulation.extract_by_regex import ExtractByRegex


class TestExtractByRegex:
    def test_extracts_and_flattens_all_matches(self):
        plugin = ExtractByRegex(options=r'{"regex": "\\d+"}')
        result = plugin.run(["order 12 and 34", "item 5"])

        assert result == ["12", "34", "5"]

    def test_omits_lines_with_no_match(self):
        plugin = ExtractByRegex(options=r'{"regex": "\\d+"}')
        result = plugin.run(["order 12", "no numbers", "item 5"])

        assert result == ["12", "", "5"]

    def test_returns_full_matches_not_capture_groups(self):
        plugin = ExtractByRegex(options=r'{"regex": "id:(\\d+)"}')
        result = plugin.run(["id:42"])

        assert result == ["id:42"]

    def test_empty_regex_returns_error(self):
        plugin = ExtractByRegex()
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result
        assert "no regex provided" in result

    def test_invalid_regex_returns_error(self):
        plugin = ExtractByRegex(options='{"regex": "["}')
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result

    def test_preserves_empty_lines(self):
        plugin = ExtractByRegex(options=r'{"regex": "\\w+"}')
        result = plugin.run(["", "hello"])

        assert result == ["", "hello"]
