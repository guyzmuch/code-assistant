import json

from plugins.commons.json.stringify_json import StringifyJson

EXPECTED_PRETTY = """{
  "a": 1,
  "b": "foo"
}"""


EXPECTED_JOHN = """{
  "age": 30,
  "car": null,
  "name": "John"
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

    def test_extracts_json_from_html_attribute(self):
        plugin = StringifyJson()
        result = plugin.run(
            [
                '<p class="foo" metadata="{\\"name\\":\\"John\\", \\"age\\":30, \\"car\\":null};">foobare</p>'
            ]
        )[0]

        assert result == EXPECTED_JOHN

    def test_extracts_json_from_javascript_call(self):
        plugin = StringifyJson()
        result = plugin.run(
            ['myFunc("plop", {"name":"John", "age":30, "car":null}, plip)']
        )[0]

        assert result == EXPECTED_JOHN

    def test_extracts_json_from_multiline_javascript_call(self):
        plugin = StringifyJson()
        result = plugin.run(
            [
                'myFunc(',
                '  "plop", ',
                '  {"name":"John", "age":30, "car":null}, ',
                '  plip',
                ')'
            ]
        )[0]

        assert result == EXPECTED_JOHN
