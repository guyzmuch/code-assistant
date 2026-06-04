from utils.format import format_section, json_dumps, parse_json_lenient


def test_format_section_returns_header_line():
    assert format_section("HEADER") == "--- HEADER"


class TestJsonDumps:
    def test_pretty_output(self):
        assert json_dumps({"b": 2, "a": 1}, pretty=True) == """{
  "a": 1,
  "b": 2
}"""

    def test_compact_output(self):
        assert json_dumps({"b": 2, "a": 1}, pretty=False) == '{"a":1,"b":2}'


class TestParseJsonLenient:
    def test_parses_normal_json(self):
        assert parse_json_lenient('{"a": 1}') == {"a": 1}

    def test_parses_over_stringified_json(self):
        assert parse_json_lenient(r'{\n  \"a\": 1}') == {"a": 1}

    def test_parses_json_wrapped_in_json_string(self):
        assert parse_json_lenient('"{\\"a\\": 1}"') == {"a": 1}
