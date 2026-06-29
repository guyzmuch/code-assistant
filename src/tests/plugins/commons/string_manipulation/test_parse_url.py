from plugins.commons.string_manipulation.parse_url import ParseUrl

SAMPLE_URL = (
    "https://www.w3schools.com/html/default.asp?para1=value1&para2=value2#section1"
)

EXPECTED_FULL_URL_JSON = """{
  "fragment": "section1",
  "hostname": "www.w3schools.com",
  "href": "https://www.w3schools.com/html/default.asp?para1=value1&para2=value2#section1",
  "netloc": "www.w3schools.com",
  "password": null,
  "path": "/html/default.asp",
  "path_parts": [
    "html",
    "default.asp"
  ],
  "port": null,
  "query": {
    "para1": "value1",
    "para2": "value2"
  },
  "scheme": "https",
  "username": null
}"""

EXPECTED_QUERY_ONLY_JSON = """{
  "para1": "value1",
  "para2": "value2"
}"""


class TestParseUrl:
    def test_parses_full_url_by_default(self):
        plugin = ParseUrl()
        result = plugin.run([SAMPLE_URL])[0]

        assert result == EXPECTED_FULL_URL_JSON

    def test_query_only_returns_query_object(self):
        plugin = ParseUrl(options='{"query_only": true}')
        result = plugin.run([SAMPLE_URL])[0]

        assert result == EXPECTED_QUERY_ONLY_JSON

    def test_merges_multiline_input_into_one_url(self):
        plugin = ParseUrl()
        result = plugin.run(
            [
                "https://example.com/path?",
                "name=john&city=nyc#top",
            ]
        )[0]

        assert '"href": "https://example.com/path?name=john&city=nyc#top"' in result
        assert '"query": {\n    "city": "nyc",\n    "name": "john"\n  }' in result

    def test_decodes_query_values_and_handles_duplicate_keys(self):
        plugin = ParseUrl(
            options='{"query_only": true}',
        )
        result = plugin.run(
            [
                "https://user:pass@example.com:8080/items?"
                "q=hello%20world&tag=a&tag=b",
            ]
        )[0]

        assert result == """{
  "q": "hello world",
  "tag": [
    "a",
    "b"
  ]
}"""

    def test_splits_path_into_parts_for_readability(self):
        plugin = ParseUrl()
        result = plugin.run(
            ["https://example.com/api/v1/users/123/profile"]
        )[0]

        assert '"path": "/api/v1/users/123/profile"' in result
        assert '"path_parts": [\n    "api",\n    "v1",\n    "users",\n    "123",\n    "profile"\n  ]' in result

    def test_path_parts_empty_for_root_path(self):
        plugin = ParseUrl()
        result = plugin.run(["https://example.com/"])[0]

        assert '"path": "/"' in result
        assert '"path_parts": []' in result

    def test_exposes_auth_host_and_port_in_full_url_mode(self):
        plugin = ParseUrl()
        result = plugin.run(
            ["https://user:pass@example.com:8080/dashboard"]
        )[0]

        assert '"hostname": "example.com"' in result
        assert '"port": 8080' in result
        assert '"username": "user"' in result
        assert '"password": "pass"' in result
        assert '"netloc": "user:pass@example.com:8080"' in result

    def test_empty_input_returns_error(self):
        plugin = ParseUrl()
        result = plugin.run([])[0]

        assert "--- ERROR" in result
        assert "no input provided" in result

    def test_whitespace_only_input_returns_error(self):
        plugin = ParseUrl()
        result = plugin.run(["   ", ""])[0]

        assert "--- ERROR" in result
        assert "no non-empty input found" in result
