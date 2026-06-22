import json

from plugins.commons.json.stringify_json import StringifyJson

EXPECTED_PRETTY = """{
  "a": 1,
  "b": "foo"
}"""


class TestStringifyJson:
    def test_pretty_formats_sorted_keys(self):
        plugin = StringifyJson()
        result = plugin.run(['{"b":"foo","a":1}'])[0]

        assert result == EXPECTED_PRETTY

    def test_pretty_multiline_input(self):
        plugin = StringifyJson()
        result = plugin.run(["{", '"b": "foo",', '"a": 1', "}"])[0]

        assert result == EXPECTED_PRETTY

    def test_formats_array(self):
        plugin = StringifyJson()
        result = plugin.run(["[3, 1, 2]"])[0]

        assert result == json.dumps([3, 1, 2], indent=2, sort_keys=True)

    def test_over_stringified_json_with_literal_escapes(self):
        plugin = StringifyJson()
        result = plugin.run([r'{\n  \"b\":\"foo\",\n  \"a\":1\n}'])[0]

        assert result == EXPECTED_PRETTY

    def test_empty_input_returns_error(self):
        plugin = StringifyJson()
        result = plugin.run([])[0]

        assert "--- ERROR" in result
        assert "no input provided" in result

    def test_whitespace_only_returns_error(self):
        plugin = StringifyJson()
        result = plugin.run(["   ", ""])[0]

        assert "--- ERROR" in result
        assert "no non-empty input found" in result

    def test_invalid_json_returns_error(self):
        plugin = StringifyJson()
        result = plugin.run(["not json"])[0]

        assert "--- ERROR" in result
