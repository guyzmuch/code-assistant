from plugins.commons.string_manipulation.validate_by_regex import ValidateByRegex


class TestValidateByRegex:
    def test_outputs_valid_or_invalid_per_line(self):
        plugin = ValidateByRegex(
            options=r'{"regex": "^[\\w.+-]+@[\\w.-]+\\.[a-zA-Z]{2,}$"}'
        )
        result = plugin.run(
            ["alice@example.com", "not-an-email", "bob@example.org"]
        )

        assert result == ["valid", "invalid", "valid"]

    def test_matches_anywhere_on_line(self):
        plugin = ValidateByRegex(options=r'{"regex": "\\d+"}')
        result = plugin.run(["order 12", "no numbers"])

        assert result == ["valid", "invalid"]

    def test_empty_regex_returns_error(self):
        plugin = ValidateByRegex()
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result
        assert "no regex provided" in result

    def test_invalid_regex_returns_error(self):
        plugin = ValidateByRegex(options='{"regex": "["}')
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result

    def test_preserves_empty_lines(self):
        plugin = ValidateByRegex(options=r'{"regex": "\\w+"}')
        result = plugin.run(["", "hello"])

        assert result == ["", "valid"]
