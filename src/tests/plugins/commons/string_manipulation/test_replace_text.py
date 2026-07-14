import pytest

from plugins.commons.string_manipulation.replace_text import (
    ReplaceText,
    parse_search_pattern,
    replace_in_line,
)


class TestParseSearchPattern:
    def test_plain_text_is_literal(self):
        is_regex, pattern = parse_search_pattern("hello")

        assert is_regex is False
        assert pattern == "hello"

    def test_double_quoted_raw_string_is_regex(self):
        is_regex, pattern = parse_search_pattern(r'r"\d+"')

        assert is_regex is True
        assert pattern == r"\d+"

    def test_single_quoted_raw_string_is_regex(self):
        is_regex, pattern = parse_search_pattern("r'foo|bar'")

        assert is_regex is True
        assert pattern == "foo|bar"

    def test_invalid_raw_string_raises(self):
        with pytest.raises(ValueError, match="invalid regex literal"):
            parse_search_pattern('r"unclosed')


class TestReplaceInLine:
    def test_literal_replace(self):
        result = replace_in_line(
            "foo bar foo",
            is_regex=False,
            pattern="foo",
            replacement="baz",
            case_sensitive=True,
        )

        assert result == "baz bar baz"

    def test_literal_replace_case_insensitive(self):
        result = replace_in_line(
            "Foo BAR foo",
            is_regex=False,
            pattern="foo",
            replacement="baz",
        )

        assert result == "baz BAR baz"

    def test_regex_replace(self):
        result = replace_in_line(
            "order 42",
            is_regex=True,
            pattern=r"\d+",
            replacement="XX",
            case_sensitive=True,
        )

        assert result == "order XX"


class TestReplaceText:
    def test_literal_replace_per_line(self):
        plugin = ReplaceText(options='{"search": "foo", "replace": "bar"}')
        result = plugin.run(["foo baz", "no match", "foo foo"])

        assert result == ["bar baz", "no match", "bar bar"]

    def test_literal_replace_is_case_insensitive_by_default(self):
        plugin = ReplaceText(options='{"search": "foo", "replace": "bar"}')
        result = plugin.run(["Foo baz", "FOO FOO"])

        assert result == ["bar baz", "bar bar"]

    def test_literal_replace_respects_case_sensitive_option(self):
        plugin = ReplaceText(
            options='{"search": "foo", "replace": "bar", "case_sensitive": true}'
        )
        result = plugin.run(["Foo baz", "foo foo"])

        assert result == ["Foo baz", "bar bar"]

    def test_regex_replace_is_case_insensitive_by_default(self):
        plugin = ReplaceText(options=r'{"search": "r\"HELLO\"", "replace": "hi"}')
        result = plugin.run(["hello world", "HELLO there"])

        assert result == ["hi world", "hi there"]

    def test_regex_replace_per_line(self):
        plugin = ReplaceText(options=r'{"search": "r\"\\d+\"", "replace": "#"}')
        result = plugin.run(["item 1", "no digits", "x99y"])

        assert result == ["item #", "no digits", "x#y"]

    def test_regex_backreference(self):
        plugin = ReplaceText(
            options=r'{"search": "r\"(\\d+)\"", "replace": "[\\1]"}'
        )
        result = plugin.run(["order 42"])

        assert result == ["order [42]"]

    def test_empty_search_returns_error(self):
        plugin = ReplaceText()
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result
        assert "no search text provided" in result

    def test_invalid_regex_returns_error(self):
        plugin = ReplaceText(options='{"search": "r\"[\"", "replace": "x"}')
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result

    def test_invalid_regex_literal_returns_error(self):
        plugin = ReplaceText(options={"search": 'r"unclosed', "replace": "x"})
        result = plugin.run(["hello"])[0]

        assert "--- ERROR" in result
        assert "invalid regex literal" in result

    def test_preserves_empty_lines(self):
        plugin = ReplaceText(options='{"search": "a", "replace": "b"}')
        result = plugin.run(["a", "", "a"])

        assert result == ["b", "", "b"]
